from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError

from turku_api.models import Auth, Machine, Source, Storage

import json
import random
from datetime import timedelta


def frequency_next_scheduled(frequency, base_time=timezone.now()):
    f = frequency.split(',')

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
        target_date = (today + timedelta(weeks=1) - timedelta(days=today.isoweekday()) + timedelta(days=target_day))
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
        target_date = (today - timedelta(days=today.isoweekday()) + timedelta(days=target_day))
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


@csrf_exempt
def update_config(request):
    # Require JSON POST
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not (('CONTENT_TYPE' in request.META) and (request.META['CONTENT_TYPE'] == 'application/json')):
        return HttpResponseBadRequest('Bad Content-Type (expected application/json)')

    # Load the POSTed JSON
    try:
        req_in = json.load(request)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    # Check for global auth
    if 'auth' not in req_in:
        return HttpResponseForbidden('Bad auth')
    try:
        a = Auth.objects.get(secret=req_in['auth'], active=True)
    except Auth.DoesNotExist:
        return HttpResponseForbidden('Bad auth')
    if a.secret_type != 'machine_reg':
        return HttpResponseForbidden('Bad auth')

    if not (('machine' in req_in) and (type(req_in['machine']) == dict)):
        return HttpResponseBadRequest('"machine" dict required')
    req_machine = req_in['machine']

    # Make sure these exist in the request (validation comes later)
    for k in ('uuid', 'secret'):
        if k not in req_machine:
            return HttpResponseBadRequest('Missing required machine option "%s"' % k)

    # Create or load the machine
    try:
        m = Machine.objects.get(uuid=req_machine['uuid'], active=True)
        modified = False
    except Machine.DoesNotExist:
        m = Machine(uuid=req_machine['uuid'])
        m.secret = req_machine['secret']
        modified = True

    # XXX temporary random
    try:
        m.storage
    except Storage.DoesNotExist:
        m.storage = random.choice(Storage.objects.filter(active=True))

    # If the machine existed before, it had a secret.  Make sure that
    # hasn't changed.
    if m.secret != req_machine['secret']:
        return HttpResponseForbidden('Bad secret for existing machine')

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
            return HttpResponseBadRequest('Validation error: %s' % str(e))
        m.save()

    if 'sources' in req_in:
        req_sources = req_in['sources']
        if not type(req_sources) == dict:
            return HttpResponseBadRequest('Invalid type for "sources"')
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
        for k in ('path', 'username', 'password', 'frequency', 'comment', 'shared_service', 'snapshot', 'inplace'):
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
                return HttpResponseBadRequest('Validation error: %s' % str(e))
            s.save()

    for name in req_sources.keys():
        if name in sources_in_db:
            continue
        s = Source()
        s.name = name
        s.machine = m

        for k in ('path', 'username', 'password', 'frequency', 'comment', 'shared_service', 'snapshot', 'inplace'):
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
            return HttpResponseBadRequest('Validation error: %s' % str(e))
        s.save()

    out = {
        'ssh_ping_host': m.storage.ssh_ping_host,
        'ssh_ping_host_keys': json.loads(m.storage.ssh_ping_host_keys),
        'ssh_ping_port': m.storage.ssh_ping_port,
        'ssh_ping_user': m.storage.ssh_ping_user,
    }
    return HttpResponse(json.dumps(out), content_type='application/json')


@csrf_exempt
def storage_ping_checkin(request):
    # Require JSON POST
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not (('CONTENT_TYPE' in request.META) and (request.META['CONTENT_TYPE'] == 'application/json')):
        return HttpResponseBadRequest('Bad Content-Type (expected application/json)')

    # Load the POSTed JSON
    try:
        req_in = json.load(request)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    # Check for source auth
    for k in ('name', 'secret'):
        if k not in req_in:
            return HttpResponseForbidden('Bad auth')
    try:
        storage = Storage.objects.get(name=req_in['name'], secret=req_in['secret'], active=True)
    except Storage.DoesNotExist:
        return HttpResponseForbidden('Bad auth')

    # Make sure these exist in the request
    for k in ('machine_uuid',):
        if k not in req_in:
            return HttpResponseBadRequest('Missing required option "%s"' % k)

    # Create or load the machine
    try:
        m = Machine.objects.get(uuid=req_in['machine_uuid'], storage=storage, active=True)
    except Machine.DoesNotExist:
        return HttpResponseNotFound('Machine not found')

    scheduled_sources = []
    now = timezone.now()
    for s in m.source_set.filter(date_next_backup__lte=now, active=True):
        scheduled_sources.append({
            'name': s.name,
            'path': s.path,
            'username': s.username,
            'password': s.password,
            'exclude': json.loads(s.exclude),
            'shared_service': s.shared_service,
            'inplace': s.inplace,
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


@csrf_exempt
def storage_ping_source_update(request):
    # Require JSON POST
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not (('CONTENT_TYPE' in request.META) and (request.META['CONTENT_TYPE'] == 'application/json')):
        return HttpResponseBadRequest('Bad Content-Type (expected application/json)')

    # Load the POSTed JSON
    try:
        req_in = json.load(request)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    # Check for source auth
    for k in ('name', 'secret'):
        if k not in req_in:
            return HttpResponseForbidden('Bad auth')
    try:
        storage = Storage.objects.get(name=req_in['name'], secret=req_in['secret'], active=True)
    except Storage.DoesNotExist:
        return HttpResponseForbidden('Bad auth')

    # Make sure these exist in the request
    for k in ('machine_uuid',):
        if k not in req_in:
            return HttpResponseBadRequest('Missing required option "%s"' % k)

    # Create or load the machine
    try:
        m = Machine.objects.get(uuid=req_in['machine_uuid'], storage=storage, active=True)
    except Machine.DoesNotExist:
        return HttpResponseNotFound('Machine not found')

    try:
        s = m.source_set.get(name=req_in['source_name'], active=True)
    except Source.DoesNotExist:
        return HttpResponseNotFound('Source not found')
    if req_in['success']:
        s.date_last_backed_up = timezone.now()
        s.date_next_backup = frequency_next_scheduled(s.frequency)
        s.save()
    return HttpResponse(json.dumps({}), content_type='application/json')
