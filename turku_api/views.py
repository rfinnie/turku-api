from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError

from turku_api.models import Auth, Machine, Source, Storage

import json
import random
from datetime import timedelta


def frequency_next_scheduled(frequency, base_time=None):
    if not base_time:
        base_time = timezone.now()
    f = [x.strip() for x in frequency.split(',')]

    if f[0] == 'hourly':
        target_time = (base_time.replace(minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0) + timedelta(hours=1))
        # Push it out 10 minutes if it falls within 10 minutes of now
        if target_time < (base_time + timedelta(minutes=10)):
            target_time = (target_time + timedelta(minutes=10))
        return target_time

    today = base_time.replace(hour=0, minute=0, second=0, microsecond=0)
    if f[0] == 'daily':
        # Tomorrow
        target_date = (today + timedelta(days=1))
    elif f[0] == 'weekly':
        # Random day next week
        target_day = random.randint(0, 6)
        target_date = (today + timedelta(weeks=1) - timedelta(days=((today.weekday() + 1) % 7)) + timedelta(days=target_day))
        # Push it out 3 days if it falls within 3 days of now
        if target_date < (base_time + timedelta(days=3)):
            target_date = (target_date + timedelta(days=3))
    elif f[0] in ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'):
        # Next Xday
        day_map = {
            'sunday': 0,
            'monday': 1,
            'tuesday': 2,
            'wednesday': 3,
            'thursday': 4,
            'friday': 5,
            'saturday': 6,
        }
        target_day = day_map[f[0]]
        target_date = (today - timedelta(days=((today.weekday() + 1) % 7)) + timedelta(days=target_day))
        if target_date < today:
            target_date = (target_date + timedelta(weeks=1))
    elif f[0] == 'monthly':
        next_month = (today.replace(day=1) + timedelta(days=40)).replace(day=1)
        month_after = (next_month.replace(day=1) + timedelta(days=40)).replace(day=1)
        target_date = (next_month + timedelta(days=random.randint(1, (month_after - next_month).days)))
        # Push it out a week if it falls within a week of now
        if target_date < (base_time + timedelta(days=7)):
            target_date = (target_date + timedelta(days=7))
    else:
        # Fall back to tomorrow
        target_date = (today + timedelta(days=1))

    if len(f) == 1:
        return (target_date + timedelta(seconds=random.randint(0, 86399)))
    time_range = f[1].split('-')
    start = (int(time_range[0][0:2]) * 60 * 60) + (int(time_range[0][2:4]) * 60)
    if len(time_range) == 1:
        return (target_date + timedelta(seconds=start))
    end = (int(time_range[1][0:2]) * 60 * 60) + (int(time_range[1][2:4]) * 60)
    if start > end:
        # Invalid range
        return (target_date + timedelta(seconds=random.randint(0, 86399)))
    return (target_date + timedelta(seconds=random.randint(start, end)))


class HttpResponseException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ViewV1():
    def __init__(self, django_request):
        self.django_request = django_request
        self._parse_json_post()

    def _parse_json_post(self):
        # Require JSON POST
        if not self.django_request.method == 'POST':
            raise HttpResponseException(HttpResponseNotAllowed(['POST']))
        if not (('CONTENT_TYPE' in self.django_request.META) and (self.django_request.META['CONTENT_TYPE'] == 'application/json')):
            raise HttpResponseException(HttpResponseBadRequest('Bad Content-Type (expected application/json)'))

        # Load the POSTed JSON
        try:
            self.req = json.load(self.django_request)
        except ValueError as e:
            raise HttpResponseException(HttpResponseBadRequest(str(e)))

    def _storage_authenticate(self):
        # Check for storage auth
        for k in ('name', 'secret'):
            if k not in self.req:
                raise HttpResponseException(HttpResponseForbidden('Bad auth'))
        try:
            self.storage = Storage.objects.get(name=self.req['name'], secret=self.req['secret'], active=True)
        except Storage.DoesNotExist:
            raise HttpResponseException(HttpResponseForbidden('Bad auth'))

    def _storage_get_machine(self):
        # Make sure these exist in the request
        for k in ('machine_uuid',):
            if k not in self.req:
                raise HttpResponseException(HttpResponseBadRequest('Missing required option "%s"' % k))

        # Create or load the machine
        try:
            return Machine.objects.get(uuid=self.req['machine_uuid'], storage=self.storage, active=True)
        except Machine.DoesNotExist:
            raise HttpResponseException(httpResponseNotFound('Machine not found'))

    def update_config(self):
        # Check for global auth
        if 'auth' not in self.req:
            raise HttpResponseException(HttpResponseForbidden('Bad auth'))
        try:
            a = Auth.objects.get(secret=self.req['auth'], secret_type='machine_reg', active=True)
        except Auth.DoesNotExist:
            raise HttpResponseException(HttpResponseForbidden('Bad auth'))

        if not (('machine' in self.req) and (type(self.req['machine']) == dict)):
            raise HttpResponseException(HttpResponseBadRequest('"machine" dict required'))
        req_machine = self.req['machine']

        # Make sure these exist in the request (validation comes later)
        for k in ('uuid', 'secret'):
            if k not in req_machine:
                raise HttpResponseException(HttpResponseBadRequest('Missing required machine option "%s"' % k))

        # Create or load the machine
        try:
            m = Machine.objects.get(uuid=req_machine['uuid'], active=True)
            modified = False
        except Machine.DoesNotExist:
            m = Machine(uuid=req_machine['uuid'])
            m.secret = req_machine['secret']
            m.auth = a
            modified = True

        new_storage_needed = False
        try:
            m.storage
        except Storage.DoesNotExist:
            new_storage_needed = True
        if new_storage_needed:
            try:
               # XXX temporary random
                m.storage = random.choice(Storage.objects.filter(active=True))
                modified = True
            except IndexError:
                raise HttpResponseException(HttpResponseNotFound('No storages are currently available'))

        # If the machine existed before, it had a secret.  Make sure that
        # hasn't changed.
        if m.secret != req_machine['secret']:
            raise HttpResponseException(HttpResponseForbidden('Bad secret for existing machine'))

        # If the registration secret changed, update it
        if m.auth.secret != a.secret:
            m.auth = a
            modified = True

        # If any of these exist in the request, add or update them in the
        # machine.
        for k in ('environment_name', 'service_name', 'unit_name', 'comment', 'ssh_public_key'):
            if (k in req_machine) and (getattr(m, k) != req_machine[k]):
                setattr(m, k, req_machine[k])
                modified = True

        # Validate/save if modified
        if modified:
            m.date_updated = timezone.now()
            try:
                m.full_clean()
            except ValidationError as e:
                raise HttpResponseException(HttpResponseBadRequest('Validation error: %s' % str(e)))
            m.save()

        if 'sources' in self.req:
            req_sources = self.req['sources']
            if not type(req_sources) == dict:
                raise HttpResponseException(HttpResponseBadRequest('Invalid type for "sources"'))
        else:
            req_sources = {}

        sources_in_db = []
        for s in m.source_set.all():
            if s.name not in req_sources:
                s.active = False
                s.save()
                continue
            sources_in_db.append(s.name)

            modified = False
            for k in ('path', 'username', 'password', 'frequency', 'retention', 'comment', 'shared_service', 'large_rotating_files', 'large_modifying_files'):
                if (k in req_sources[s.name]) and (getattr(s, k) != req_sources[s.name][k]):
                    setattr(s, k, req_sources[s.name][k])
                    if k == 'frequency':
                        s.date_next_backup = frequency_next_scheduled(req_sources[s.name][k])
                    modified = True
            for k in ('exclude',):
                if k not in req_sources[s.name]:
                    continue
                v = json.dumps(req_sources[s.name][k], sort_keys=True)
                if getattr(s, k) != v:
                    setattr(s, k, v)
                    modified = True

            if modified:
                s.active = True
                s.date_updated = timezone.now()
                try:
                    s.full_clean()
                except ValidationError as e:
                    raise HttpResponseException(HttpResponseBadRequest('Validation error: %s' % str(e)))
                s.save()

        for name in req_sources.keys():
            if name in sources_in_db:
                continue
            s = Source()
            s.name = name
            s.machine = m

            for k in ('path', 'username', 'password', 'frequency', 'retention', 'comment', 'shared_service', 'large_rotating_files', 'large_modifying_files'):
                if k not in req_sources[s.name]:
                    continue
                setattr(s, k, req_sources[s.name][k])
                if k == 'frequency':
                    s.date_next_backup = frequency_next_scheduled(req_sources[s.name][k])
            for k in ('exclude',):
                if k not in req_sources[s.name]:
                    continue
                v = json.dumps(req_sources[s.name][k], sort_keys=True)
                setattr(s, k, v)

            try:
                s.full_clean()
            except ValidationError as e:
                raise HttpResponseException(HttpResponseBadRequest('Validation error: %s' % str(e)))
            s.save()

        out = {
            'storage_name': m.storage.name,
            'ssh_ping_host': m.storage.ssh_ping_host,
            'ssh_ping_host_keys': json.loads(m.storage.ssh_ping_host_keys),
            'ssh_ping_port': m.storage.ssh_ping_port,
            'ssh_ping_user': m.storage.ssh_ping_user,
        }
        return HttpResponse(json.dumps(out), content_type='application/json')

    def storage_ping_checkin(self):
        self._storage_authenticate()
        m = self._storage_get_machine()

        scheduled_sources = []
        now = timezone.now()
        for s in m.source_set.filter(date_next_backup__lte=now, active=True):
            scheduled_sources.append({
                'name': s.name,
                'path': s.path,
                'username': s.username,
                'password': s.password,
                'retention': s.retention,
                'exclude': json.loads(s.exclude),
                'shared_service': s.shared_service,
                'large_rotating_files': s.large_rotating_files,
                'large_modifying_files': s.large_modifying_files,
            })

        out = {
            'machine': {
                'uuid': m.uuid,
                'environment_name': m.environment_name,
                'service_name': m.service_name,
                'unit_name': m.unit_name,
            },
            'scheduled_sources': scheduled_sources,
        }
        m.date_checked_in = now
        m.save()
        return HttpResponse(json.dumps(out), content_type='application/json')

    def storage_ping_source_update(self):
        self._storage_authenticate()
        m = self._storage_get_machine()

        try:
            s = m.source_set.get(name=self.req['source_name'], active=True)
        except Source.DoesNotExist:
            raise HttpResponseException(HttpResponseNotFound('Source not found'))
        if self.req['success']:
            s.date_last_backed_up = timezone.now()
            s.date_next_backup = frequency_next_scheduled(s.frequency)
            s.save()
        return HttpResponse(json.dumps({}), content_type='application/json')

    def storage_update_config(self):
        # Check for global auth
        if 'auth' not in self.req:
            raise HttpResponseException(HttpResponseForbidden('Bad auth'))
        try:
            a = Auth.objects.get(secret=self.req['auth'], secret_type='storage_reg', active=True)
        except Auth.DoesNotExist:
            raise HttpResponseException(HttpResponseForbidden('Bad auth'))

        if not (('storage' in self.req) and (type(self.req['storage']) == dict)):
            raise HttpResponseException(HttpResponseBadRequest('"storage" dict required'))
        req_storage = self.req['storage']

        # Make sure these exist in the request (validation comes later)
        for k in ('name', 'secret', 'ssh_ping_host', 'ssh_ping_port', 'ssh_ping_user', 'ssh_ping_host_keys'):
            if k not in req_storage:
                raise HttpResponseException(HttpResponseBadRequest('Missing required storage option "%s"' % k))

        # Create or load the storage
        try:
            self.storage = Storage.objects.get(name=req_storage['name'], active=True)
            modified = False
        except Storage.DoesNotExist:
            self.storage = Storage(name=req_storage['name'])
            self.storage.secret = req_storage['secret']
            self.storage.auth = a
            modified = True

        # If the storage existed before, it had a secret.  Make sure that
        # hasn't changed.
        if self.storage.secret != req_storage['secret']:
            raise HttpResponseException(HttpResponseForbidden('Bad secret for existing storage'))

        # If the registration secret changed, update it
        if self.storage.auth.secret != a.secret:
            self.storage.auth = a
            modified = True

        # If any of these exist in the request, add or update them in the
        # self.storage.
        for k in ('comment', 'ssh_ping_host', 'ssh_ping_port', 'ssh_ping_user'):
            if (k in req_storage) and (getattr(self.storage, k) != req_storage[k]):
                setattr(self.storage, k, req_storage[k])
                modified = True

        for k in ('ssh_ping_host_keys',):
            if k not in req_storage:
                continue
            v = json.dumps(req_storage[k], sort_keys=True)
            if getattr(self.storage, k) != v:
                setattr(self.storage, k, v)
                modified = True

        # Validate if modified
        if modified:
            self.storage.date_updated = timezone.now()
            try:
                self.storage.full_clean()
            except ValidationError as e:
                raise HttpResponseException(HttpResponseBadRequest('Validation error: %s' % str(e)))

        self.storage.date_checked_in = timezone.now()
        self.storage.save()

        machines = {}
        for m in Machine.objects.filter(storage=self.storage, active=True):
            machines[m.uuid] = {
                'environment_name': m.environment_name,
                'service_name': m.service_name,
                'unit_name': m.unit_name,
                'comment': m.comment,
                'ssh_public_key': m.ssh_public_key,
            }
        return HttpResponse(json.dumps({'machines': machines}), content_type='application/json')


@csrf_exempt
def update_config(request):
    try:
        return ViewV1(request).update_config()
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
