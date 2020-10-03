# Turku backups - API server
# Copyright 2015 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the Affero GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

import binascii
from datetime import datetime, timedelta
import json
import random

from django.contrib.auth import hashers
from django.core.exceptions import ValidationError
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

try:
    from turku_api.croniter_hash import croniter_hash
except ImportError as e:
    # We only want to raise this import error if cron format is
    # attempted by the client
    croniter_hash = e

from turku_api.models import Auth, BackupLog, FilterSet, Machine, Source, Storage


def hashedint(a, b, hash_id=""):
    """ID-hashed drop-in replacement for random.randint"""

    if isinstance(hash_id, bytes):
        id_bytes = hash_id
    elif isinstance(hash_id, str):
        id_bytes = hash_id.encode("UTF-8")
    else:
        raise TypeError("id must be bytes or UTF-8 string")

    crc = binascii.crc32(id_bytes) & 0xFFFFFFFF
    return (crc % (b - a + 1)) + a


def frequency_next_scheduled(frequency, source_id, base_time=None):
    """Return the next scheduled datetime, given a frequency definition

    Examples of English definitions:
        "hourly", "daily", "weekly", "sunday", "monday", "tuesday",
        "wednesday", "thursday", "friday", "saturday"
    Within a specific time range: "daily, 0800-1600"
    These definitions will return a randomly-hashed time within the
    definition each time.

    If croniter is installed, "cron" plus a cron definition can be used:
        "cron 42 8 * * *"
    Or a Jenkins-style hashed cron definition, consistently hashed
    against the source ID:
        "cron H H(8-16) * * *"
    Or randomized:
        "cron R R(8-16) * * *"
    """
    if not base_time:
        base_time = timezone.now()

    if frequency.startswith("cron"):
        if isinstance(croniter_hash, ImportError):
            # croniter is not installed
            raise croniter_hash
        cron_schedule = " ".join(frequency.split(" ")[1:])
        croniter_def = croniter_hash(
            cron_schedule, start_time=base_time, hash_id=source_id
        )
        return croniter_def.get_next(datetime).replace(
            second=hashedint(0, 59, source_id)
        )

    f = [x.strip() for x in frequency.split(",")]

    if f[0] == "hourly":
        target_time = (
            base_time.replace(
                minute=hashedint(0, 59, source_id),
                second=hashedint(0, 59, source_id),
                microsecond=0,
            )
            + timedelta(hours=1)
        )
        return target_time

    today = base_time.replace(hour=0, minute=0, second=0, microsecond=0)
    if f[0] == "daily":
        # Tomorrow
        target_date = today + timedelta(days=1)
    elif f[0] == "weekly":
        # Hashed day next week
        target_day = hashedint(0, 6, source_id)
        target_date = (
            today
            + timedelta(weeks=1)
            - timedelta(days=((today.weekday() + 1) % 7))
            + timedelta(days=target_day)
        )
    elif f[0] in (
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ):
        # Next Xday
        day_map = {
            "sunday": 0,
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5,
            "saturday": 6,
        }
        target_day = day_map[f[0]]
        target_date = (
            today
            - timedelta(days=((today.weekday() + 1) % 7))
            + timedelta(days=target_day)
        )
        if target_date < today:
            target_date = target_date + timedelta(weeks=1)
    elif f[0] == "monthly":
        next_month = (today.replace(day=1) + timedelta(days=40)).replace(day=1)
        month_after = (next_month.replace(day=1) + timedelta(days=40)).replace(day=1)
        target_date = next_month + timedelta(
            days=hashedint(1, (month_after - next_month).days, source_id)
        )
    else:
        # Fall back to daily
        target_date = today + timedelta(days=1)

    if len(f) == 1:
        return target_date + timedelta(seconds=hashedint(0, 86399, source_id))
    time_range = f[1].split("-")
    start = (int(time_range[0][0:2]) * 60 * 60) + (int(time_range[0][2:4]) * 60)
    if len(time_range) == 1:
        # Not a range
        return target_date + timedelta(seconds=start)
    end = (int(time_range[1][0:2]) * 60 * 60) + (int(time_range[1][2:4]) * 60)
    if end < start:
        # Day rollover
        end = end + 86400
    return target_date + timedelta(seconds=hashedint(start, end, source_id))


def random_weighted(m):
    """Return a weighted random key."""
    total = sum(m.values())
    if total <= 0:
        return random.choice(list(m.keys()))
    weighted = []
    tp = 0
    for (k, v) in m.items():
        tp = tp + (float(v) / float(total))
        weighted.append((k, tp))
    r = random.random()
    for (k, v) in weighted:
        if r < v:
            return k


def get_repo_revision():
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(base_dir, ".bzr")):
        try:
            import bzrlib.errors
            from bzrlib.branch import Branch
        except ImportError:
            return None
        try:
            branch = Branch.open(base_dir)
        except bzrlib.errors.NotBranchError:
            return None
        return branch.last_revision_info()[0]


class HttpResponseException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ViewV1:
    def __init__(self, django_request):
        self.django_request = django_request
        self._parse_json_post()

    def _parse_json_post(self):
        # Require JSON POST
        if not self.django_request.method == "POST":
            raise HttpResponseException(HttpResponseNotAllowed(["POST"]))
        if not (
            ("CONTENT_TYPE" in self.django_request.META)
            and (self.django_request.META["CONTENT_TYPE"] == "application/json")
        ):
            raise HttpResponseException(
                HttpResponseBadRequest("Bad Content-Type (expected application/json)")
            )

        # Load the POSTed JSON
        try:
            self.req = json.load(self.django_request)
        except ValueError as e:
            raise HttpResponseException(HttpResponseBadRequest(str(e)))

    def storage_login(self, is_update_config=False):
        """Authenticate a Storage login"""

        if "storage" not in self.req:
            raise HttpResponseException(
                HttpResponseBadRequest('Missing required option "storage"')
            )
        for k in ("name", "secret"):
            if k not in self.req["storage"]:
                raise HttpResponseException(HttpResponseForbidden("Bad auth"))
        try:
            storage = Storage.objects.get(name=self.req["storage"]["name"], active=True)
        except Storage.DoesNotExist:
            if is_update_config:
                return
            else:
                raise HttpResponseException(HttpResponseForbidden("Bad auth"))
        if not hashers.check_password(
            self.req["storage"]["secret"], storage.secret_hash
        ):
            raise HttpResponseException(HttpResponseForbidden("Bad auth"))

        return storage

    def storage_get_machine(self, storage):
        """Get a Machine associated with a Storage request"""

        if "machine" not in self.req:
            raise HttpResponseException(
                HttpResponseBadRequest('Missing required option "machine"')
            )
        if "uuid" not in self.req["machine"]:
            raise HttpResponseException(
                HttpResponseBadRequest('Missing required option "machine.uuid"')
            )

        # Create or load the machine
        try:
            return Machine.objects.get(
                uuid=self.req["machine"]["uuid"],
                storage=storage,
                active=True,
                published=True,
            )
        except Machine.DoesNotExist:
            raise HttpResponseException(HttpResponseNotFound("Machine not found"))

    def machine_login(self, is_update_config=False):
        """Authenticate a Machine login"""

        if not (("machine" in self.req) and (isinstance(self.req["machine"], dict))):
            raise HttpResponseException(
                HttpResponseBadRequest('"machine" dict required')
            )

        # Make sure these exist in the request (validation comes later)
        for k in ("uuid", "secret"):
            if k not in self.req["machine"]:
                raise HttpResponseException(
                    HttpResponseBadRequest('Missing required machine option "%s"' % k)
                )

        # Load the machine
        try:
            machine = Machine.objects.get(uuid=self.req["machine"]["uuid"], active=True)
        except Machine.DoesNotExist:
            if is_update_config:
                return
            else:
                # Return Forbidden for nonexistent Machines to avoid
                # existence leaking
                raise HttpResponseException(HttpResponseForbidden("Bad auth"))
        if (not is_update_config) and (not machine.published):
            raise HttpResponseException(HttpResponseForbidden("Bad auth"))
        if not hashers.check_password(
            self.req["machine"]["secret"], machine.secret_hash
        ):
            raise HttpResponseException(HttpResponseForbidden("Bad auth"))

        return machine

    def get_registration_auth(self, secret_type):
        # Check for global auth
        if "auth" not in self.req:
            raise HttpResponseException(HttpResponseForbidden("Bad auth"))
        if isinstance(self.req["auth"], dict):
            if not (("name" in self.req["auth"]) and ("secret" in self.req["auth"])):
                raise HttpResponseException(HttpResponseForbidden("Bad auth"))
            try:
                a = Auth.objects.get(
                    name=self.req["auth"]["name"], secret_type=secret_type, active=True
                )
            except Auth.DoesNotExist:
                raise HttpResponseException(HttpResponseForbidden("Bad auth"))
            if hashers.check_password(self.req["auth"]["secret"], a.secret_hash):
                return a
        else:
            # XXX inefficient but temporary (legacy)
            for a in Auth.objects.filter(secret_type=secret_type, active=True):
                if hashers.check_password(self.req["auth"], a.secret_hash):
                    return a
        raise HttpResponseException(HttpResponseForbidden("Bad auth"))

    def update_config(self):
        machine = self.machine_login(is_update_config=True)
        req_machine = self.req["machine"]
        modified = False
        if machine is None:
            # machine_login failed, so go ahead with creating a new Machine
            # (but only if get_registration_auth doesn't raise)
            machine = Machine(uuid=req_machine["uuid"])
            machine.secret_hash = hashers.make_password(req_machine["secret"])
            machine.auth = self.get_registration_auth("machine_reg")
            modified = True

        # Change the machine published status if needed
        if "published" in req_machine:
            if req_machine["published"] != machine.published:
                machine.published = req_machine["published"]
                modified = True
        else:
            # If not present, default to want published
            if not machine.published:
                machine.published = True
                modified = True

        new_storage_needed = False
        try:
            machine.storage
        except Storage.DoesNotExist:
            new_storage_needed = True
        if new_storage_needed:
            try:
                weights = {}
                for storage in Storage.objects.filter(active=True, published=True):
                    weights[storage] = storage.space_available
                machine.storage = random_weighted(weights)
                modified = True
            except IndexError:
                raise HttpResponseException(
                    HttpResponseNotFound("No storages are currently available")
                )

        # If any of these exist in the request, add or update them in the
        # machine.
        for k in (
            "environment_name",
            "service_name",
            "unit_name",
            "comment",
            "ssh_public_key",
        ):
            if (k in req_machine) and (getattr(machine, k) != req_machine[k]):
                setattr(machine, k, req_machine[k])
                modified = True

        # Validate/save if modified
        if modified:
            machine.date_updated = timezone.now()
            try:
                machine.full_clean()
            except ValidationError as e:
                raise HttpResponseException(
                    HttpResponseBadRequest("Validation error: %s" % str(e))
                )
            machine.save()

        if "sources" in req_machine:
            req_sources = req_machine["sources"]
            if not isinstance(req_sources, dict):
                raise HttpResponseException(
                    HttpResponseBadRequest('Invalid type for "sources"')
                )
        elif "sources" in self.req:
            # XXX legacy
            req_sources = self.req["sources"]
            if not isinstance(req_sources, dict):
                raise HttpResponseException(
                    HttpResponseBadRequest('Invalid type for "sources"')
                )
        else:
            req_sources = {}

        sources_in_db = []
        for source in machine.source_set.all():
            if source.name not in req_sources:
                source.published = False
                source.save()
                continue
            sources_in_db.append(source.name)

            modified = False
            for k in (
                "path",
                "frequency",
                "retention",
                "comment",
                "shared_service",
                "large_rotating_files",
                "large_modifying_files",
                "bwlimit",
                "snapshot_mode",
                "preserve_hard_links",
            ):
                if (k in req_sources[source.name]) and (
                    getattr(source, k) != req_sources[source.name][k]
                ):
                    setattr(source, k, req_sources[source.name][k])
                    if k == "frequency":
                        source.date_next_backup = frequency_next_scheduled(
                            req_sources[source.name][k], source.id
                        )
                    modified = True
            for k in ("filter", "exclude"):
                if k not in req_sources[source.name]:
                    continue
                v = json.dumps(req_sources[source.name][k], sort_keys=True)
                if getattr(source, k) != v:
                    setattr(source, k, v)
                    modified = True

            if modified:
                source.published = True
                source.date_updated = timezone.now()
                try:
                    source.full_clean()
                except ValidationError as e:
                    raise HttpResponseException(
                        HttpResponseBadRequest("Validation error: %s" % str(e))
                    )
                source.save()

        for source_name in req_sources:
            if source_name in sources_in_db:
                continue
            source = Source()
            source.name = source_name
            source.machine = machine

            for k in (
                "path",
                "frequency",
                "retention",
                "comment",
                "shared_service",
                "large_rotating_files",
                "large_modifying_files",
                "bwlimit",
                "snapshot_mode",
                "preserve_hard_links",
            ):
                if k not in req_sources[source.name]:
                    continue
                setattr(source, k, req_sources[source.name][k])
            for k in ("filter", "exclude"):
                if k not in req_sources[source.name]:
                    continue
                v = json.dumps(req_sources[source.name][k], sort_keys=True)
                setattr(source, k, v)

            # New source, so schedule it regardless
            source.date_next_backup = frequency_next_scheduled(
                source.frequency, source.id
            )

            try:
                source.full_clean()
            except ValidationError as e:
                raise HttpResponseException(
                    HttpResponseBadRequest("Validation error: %s" % str(e))
                )
            source.save()

        # XXX legacy
        out = {
            "storage_name": machine.storage.name,
            "ssh_ping_host": machine.storage.ssh_ping_host,
            "ssh_ping_host_keys": json.loads(machine.storage.ssh_ping_host_keys),
            "ssh_ping_port": machine.storage.ssh_ping_port,
            "ssh_ping_user": machine.storage.ssh_ping_user,
        }
        return HttpResponse(json.dumps(out), content_type="application/json")

    def build_filters(self, set, loaded_sets=None):
        if not loaded_sets:
            loaded_sets = []
        out = []
        for f in set:
            try:
                (verb, subsetname) = f.split(" ", 1)
            except ValueError:
                continue
            if verb in ("merge", "."):
                if subsetname in loaded_sets:
                    continue
                try:
                    fs = FilterSet.objects.get(name=subsetname, active=True)
                except FilterSet.DoesNotExist:
                    continue
                for f2 in self.build_filters(json.loads(fs.filters), loaded_sets):
                    out.append(f2)
                loaded_sets.append(subsetname)
            elif verb in (
                "dir-merge",
                ":",
                "clear",
                "!",
                "exclude",
                "-",
                "include",
                "+",
                "hide",
                "H",
                "show",
                "S",
                "protect",
                "P",
                "risk",
                "R",
            ):
                out.append(f)
        return out

    def get_checkin_scheduled_sources(self, m):
        scheduled_sources = {}
        now = timezone.now()
        for source in m.source_set.filter(
            date_next_backup__lte=now, active=True, published=True
        ):
            scheduled_sources[source.name] = {
                "path": source.path,
                "retention": source.retention,
                "bwlimit": source.bwlimit,
                "filter": self.build_filters(json.loads(source.filter)),
                "exclude": json.loads(source.exclude),
                "shared_service": source.shared_service,
                "large_rotating_files": source.large_rotating_files,
                "large_modifying_files": source.large_modifying_files,
                "snapshot_mode": source.snapshot_mode,
                "preserve_hard_links": source.preserve_hard_links,
                "storage": {
                    "name": source.machine.storage.name,
                    "ssh_ping_host": source.machine.storage.ssh_ping_host,
                    "ssh_ping_host_keys": json.loads(
                        source.machine.storage.ssh_ping_host_keys
                    ),
                    "ssh_ping_port": source.machine.storage.ssh_ping_port,
                    "ssh_ping_user": source.machine.storage.ssh_ping_user,
                },
            }
        return scheduled_sources

    def agent_ping_checkin(self):
        machine = self.machine_login()
        scheduled_sources = self.get_checkin_scheduled_sources(machine)
        now = timezone.now()

        out = {"machine": {"scheduled_sources": scheduled_sources}}

        # Legacy: data hasn't been used since 2015.  However, turku-agent
        # until 2020-09-30 would check for this key and would exit if it
        # didn't exist, but would do nothing with it.
        out["scheduled_sources"] = scheduled_sources

        machine.date_checked_in = now
        machine.save()
        return HttpResponse(json.dumps(out), content_type="application/json")

    def agent_ping_restore(self):
        machine = self.machine_login()
        sources = {}
        for source in machine.source_set.filter(active=True):
            sources[source.name] = {
                "path": source.path,
                "retention": source.retention,
                "bwlimit": source.bwlimit,
                "filter": self.build_filters(json.loads(source.filter)),
                "exclude": json.loads(source.exclude),
                "shared_service": source.shared_service,
                "large_rotating_files": source.large_rotating_files,
                "large_modifying_files": source.large_modifying_files,
                "snapshot_mode": source.snapshot_mode,
                "preserve_hard_links": source.preserve_hard_links,
                "storage": {
                    "name": source.machine.storage.name,
                    "ssh_ping_host": source.machine.storage.ssh_ping_host,
                    "ssh_ping_host_keys": json.loads(
                        source.machine.storage.ssh_ping_host_keys
                    ),
                    "ssh_ping_port": source.machine.storage.ssh_ping_port,
                    "ssh_ping_user": source.machine.storage.ssh_ping_user,
                },
            }

        out = {"machine": {"sources": sources}}

        return HttpResponse(json.dumps(out), content_type="application/json")

    def storage_ping_checkin(self):
        storage = self.storage_login()
        machine = self.storage_get_machine(storage)

        scheduled_sources = self.get_checkin_scheduled_sources(machine)
        now = timezone.now()

        out = {
            "machine": {
                "uuid": machine.uuid,
                "environment_name": machine.environment_name,
                "service_name": machine.service_name,
                "unit_name": machine.unit_name,
                "scheduled_sources": scheduled_sources,
            }
        }
        machine.date_checked_in = now
        machine.save()
        return HttpResponse(json.dumps(out), content_type="application/json")

    def storage_ping_source_update(self):
        storage = self.storage_login()
        machine = self.storage_get_machine(storage)

        if "sources" not in self.req["machine"]:
            raise HttpResponseException(
                HttpResponseBadRequest('Missing required option "machine.sources"')
            )
        for source_name in self.req["machine"]["sources"]:
            source_data = self.req["machine"]["sources"][source_name]
            try:
                source = machine.source_set.get(
                    name=source_name, active=True, published=True
                )
            except Source.DoesNotExist:
                raise HttpResponseException(HttpResponseNotFound("Source not found"))
            now = timezone.now()
            is_success = "success" in source_data and source_data["success"]
            source.success = is_success
            if is_success:
                source.date_last_backed_up = now
                source.date_next_backup = frequency_next_scheduled(
                    source.frequency, source.id, now
                )
            source.save()
            backup_log = BackupLog()
            backup_log.source = source
            backup_log.date = now
            backup_log.storage = storage
            backup_log.success = is_success
            if "snapshot" in source_data:
                backup_log.snapshot = source_data["snapshot"]
            if "summary" in source_data:
                backup_log.summary = source_data["summary"]
            if "time_begin" in source_data:
                backup_log.date_begin = timezone.make_aware(
                    datetime.utcfromtimestamp(source_data["time_begin"]), timezone.utc
                )
            if "time_end" in source_data:
                backup_log.date_end = timezone.make_aware(
                    datetime.utcfromtimestamp(source_data["time_end"]), timezone.utc
                )
            backup_log.save()
        return HttpResponse(json.dumps({}), content_type="application/json")

    def storage_update_config(self):
        storage = self.storage_login(is_update_config=True)
        req_storage = self.req["storage"]

        modified = False
        if storage is None:
            # storage_login failed, so go ahead with creating a new Storage
            # (but only if get_registration_auth doesn't raise)
            storage = Storage(name=req_storage["name"])
            storage.secret_hash = hashers.make_password(req_storage["secret"])
            storage.auth = self.get_registration_auth("storage_reg")
            modified = True

        # Change the storage published status if needed
        if "published" in req_storage:
            if req_storage["published"] != storage.published:
                storage.published = req_storage["published"]
                modified = True
        else:
            # If not present, default to want published
            if not storage.published:
                storage.published = True
                modified = True

        # If any of these exist in the request, add or update them in the
        # storage.
        for k in (
            "comment",
            "ssh_ping_host",
            "ssh_ping_port",
            "ssh_ping_user",
            "space_total",
            "space_available",
        ):
            if (k in req_storage) and (getattr(storage, k) != req_storage[k]):
                setattr(storage, k, req_storage[k])
                modified = True

        for k in ("ssh_ping_host_keys",):
            if k not in req_storage:
                continue
            v = json.dumps(req_storage[k], sort_keys=True)
            if getattr(storage, k) != v:
                setattr(storage, k, v)
                modified = True

        # Validate if modified
        if modified:
            storage.date_updated = timezone.now()
            try:
                storage.full_clean()
            except ValidationError as e:
                raise HttpResponseException(
                    HttpResponseBadRequest("Validation error: %s" % str(e))
                )

        storage.date_checked_in = timezone.now()
        storage.save()

        machines = {}
        for machine in Machine.objects.filter(
            storage=storage, active=True, published=True
        ):
            machines[machine.uuid] = {
                "environment_name": machine.environment_name,
                "service_name": machine.service_name,
                "unit_name": machine.unit_name,
                "comment": machine.comment,
                "ssh_public_key": machine.ssh_public_key,
            }
        return HttpResponse(
            json.dumps({"machines": machines}), content_type="application/json"
        )


@csrf_exempt
def health(request):
    # This is a general purpose test of the API server (its ability
    # to connect to its database and serve data).  It does not
    # indicate the health of machines, storage units, etc.
    out = {
        "healthy": True,
        "date": timezone.now().isoformat(),
        "repo_revision": get_repo_revision(),
        "counts": {
            "auth": Auth.objects.count(),
            "storage": Storage.objects.count(),
            "machine": Machine.objects.count(),
            "source": Source.objects.count(),
            "filter_set": FilterSet.objects.count(),
            "backup_log": BackupLog.objects.count(),
        },
    }
    return HttpResponse(json.dumps(out), content_type="application/json")


@csrf_exempt
def update_config(request):
    try:
        return ViewV1(request).update_config()
    except HttpResponseException as e:
        return e.message


@csrf_exempt
def agent_ping_checkin(request):
    try:
        return ViewV1(request).agent_ping_checkin()
    except HttpResponseException as e:
        return e.message


@csrf_exempt
def agent_ping_restore(request):
    try:
        return ViewV1(request).agent_ping_restore()
    except HttpResponseException as e:
        return e.message


@csrf_exempt
def storage_ping_checkin(request):
    try:
        return ViewV1(request).storage_ping_checkin()
    except HttpResponseException as e:
        return e.message


@csrf_exempt
def storage_ping_source_update(request):
    try:
        return ViewV1(request).storage_ping_source_update()
    except HttpResponseException as e:
        return e.message


@csrf_exempt
def storage_update_config(request):
    try:
        return ViewV1(request).storage_update_config()
    except HttpResponseException as e:
        return e.message
