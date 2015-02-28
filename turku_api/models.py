from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import json
import uuid


def new_uuid():
    return str(uuid.uuid4())


def validate_uuid(value):
    try:
        val = str(uuid.UUID(value))
    except ValueError:
        raise ValidationError('Invalid UUID format')


def validate_json_string_list(value):
    try:
        decoded_json = json.loads(value)
    except ValueError:
        raise ValidationError('Must be a valid JSON string list')
    if not type(decoded_json) == list:
        raise ValidationError('Must be a valid JSON string list')
    for i in decoded_json:
        if not type(i) in (str, unicode):
            raise ValidationError('Must be a valid JSON string list')


class Auth(models.Model):
    SECRET_TYPES = (
        ('machine_reg', 'Machine registration'),
        ('storage_reg', 'Storage registration'),
    )
    id = models.CharField(max_length=36, primary_key=True, default=new_uuid, editable=False)
    secret = models.CharField(max_length=200, unique=True)
    secret_type = models.CharField(max_length=200, choices=SECRET_TYPES)
    comment = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        if self.comment:
            return 'Secret %s (%s)' % (self.secret, self.comment)
        else:
            return 'Secret %s' % self.secret


class Storage(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=new_uuid, editable=False)
    name = models.CharField(max_length=200, unique=True)
    secret = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, blank=True, null=True)
    ssh_ping_host = models.CharField(max_length=200)
    ssh_ping_host_keys = models.CharField(max_length=65536, default='[]', validators=[validate_json_string_list])
    ssh_ping_port = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)])
    ssh_ping_user = models.CharField(max_length=200)
    auth = models.ForeignKey(Auth)
    active = models.BooleanField(default=True)
    date_registered = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Machine(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=new_uuid, editable=False)
    uuid = models.CharField(max_length=36, unique=True, validators=[validate_uuid])
    secret = models.CharField(max_length=200)
    environment_name = models.CharField(max_length=200, blank=True, null=True)
    service_name = models.CharField(max_length=200, blank=True, null=True)
    unit_name = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, blank=True, null=True)
    ssh_public_key = models.CharField(max_length=2048)
    auth = models.ForeignKey(Auth)
    storage = models.ForeignKey(Storage)
    active = models.BooleanField(default=True)
    date_registered = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.unit_name, self.uuid)


class Source(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=new_uuid, editable=False)
    name = models.CharField(max_length=200)
    machine = models.ForeignKey(Machine)
    comment = models.CharField(max_length=200, blank=True, null=True)
    path = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    exclude = models.CharField(max_length=2048, default='[]', validators=[validate_json_string_list])
    frequency = models.CharField(max_length=200, default='daily')
    retention = models.CharField(max_length=200, default='last 5 days,earliest of month')
    shared_service = models.BooleanField(default=False)
    large_rotating_files = models.BooleanField(default=False)
    large_modifying_files = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    published = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_last_backed_up = models.DateTimeField(blank=True, null=True)
    date_next_backup = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('machine', 'name'),)

    def __unicode__(self):
        return '%s %s (%s)' % (self.machine.unit_name, self.name, self.path)
