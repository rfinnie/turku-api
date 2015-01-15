from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError

from api.models import Auth, Machine, Source, Storage

import json
import random


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
    if not 'auth' in req_in:
        return HttpResponseForbidden('Bad auth')
    try:
        a = Auth.objects.get(secret=req_in['auth'])
    except Auth.DoesNotExist:
        return HttpResponseForbidden('Bad auth')
    if a.secret_type != 'machine_reg':
        return HttpResponseForbidden('Bad auth')

    if not (('machine' in req_in) and (type(req_in['machine']) == dict)):
        return HttpResponseBadRequest('"machine" dict required')
    req_machine = req_in['machine']

    # Make sure these exist in the request (validation comes later)
    for k in ('uuid', 'secret'):
        if not k in req_machine:
            return HttpResponseBadRequest('Missing required machine option "%s"' % k)

    # Create or load the machine
    try:
        m = Machine.objects.get(id=req_machine['uuid'])
        modified = False
    except Machine.DoesNotExist:
        m = Machine(id=req_machine['uuid'])
        m.secret = req_machine['secret']
        modified = True

    # XXX temporary random
    try:
        m.storage
    except Storage.DoesNotExist:
        m.storage = random.choice(Storage.objects.all())

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
        if not s.name in req_sources:
            s.delete()
            continue
        sources_in_db.append(s.name)

        modified = False
        for k in ('path', 'username', 'password', 'frequency', 'comment', 'shared_service', 'snapshot', 'inplace'):
            if (k in req_sources[s.name]) and (getattr(s, k) != req_sources[s.name][k]):
                setattr(s, k, req_sources[s.name][k])
                modified = True
        for k in ('excludes',):
            if not k in req_sources[s.name]:
                continue
            v = json.dumps(req_sources[s.name][k], sort_keys=True)
            if getattr(s, k) != v:
                setattr(s, k, v)
                modified = True

        if modified:
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
            if not k in req_sources[s.name]:
                continue
            setattr(s, k, req_sources[s.name][k])
        for k in ('excludes',):
            if not k in req_sources[s.name]:
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
        'ssh_ping_host_key': m.storage.ssh_ping_host_key,
        'ssh_ping_port': m.storage.ssh_ping_port,
        'ssh_ping_user': m.storage.ssh_ping_user,
    }
    return HttpResponse(json.dumps(out), content_type='application/json')
