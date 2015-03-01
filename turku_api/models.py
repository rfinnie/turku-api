from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from south.modelsinspector import add_introspection_rules
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


def validate_storage_auth(value):
    try:
        a = Auth.objects.get(id=value)
    except Auth.DoesNotExist:
        raise ValidationError('Auth %s does not exist' % value)
    if a.secret_type != 'storage_reg':
        raise ValidationError('Must be a Storage registration')


def validate_machine_auth(value):
    try:
        a = Auth.objects.get(id=value)
    except Auth.DoesNotExist:
        raise ValidationError('Auth %s does not exist' % value)
    if a.secret_type != 'machine_reg':
        raise ValidationError('Must be a Machine registration')


class UuidPrimaryKeyField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(UuidPrimaryKeyField, self).__init__(*args, **kwargs)
        self.max_length = 36
        self.primary_key = True
        self.blank = True

    def get_default(self):
        import uuid
        return str(uuid.uuid4())

    def formfield(self, **kwargs):
        return None


class Auth(models.Model):
    SECRET_TYPES = (
        ('machine_reg', 'Machine registration'),
        ('storage_reg', 'Storage registration'),
    )
    id = UuidPrimaryKeyField()
    name = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    secret_type = models.CharField(max_length=200, choices=SECRET_TYPES)
    comment = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('secret', 'secret_type'),)

    def __unicode__(self):
        return self.name


class Storage(models.Model):
    id = UuidPrimaryKeyField()
    name = models.CharField(max_length=200, unique=True)
    secret_hash = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, blank=True, null=True)
    ssh_ping_host = models.CharField(max_length=200)
    ssh_ping_host_keys = models.CharField(max_length=65536, default='[]', validators=[validate_json_string_list])
    ssh_ping_port = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)])
    ssh_ping_user = models.CharField(max_length=200)
    auth = models.ForeignKey(Auth, validators=[validate_storage_auth])
    active = models.BooleanField(default=True)
    date_registered = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Machine(models.Model):
    id = UuidPrimaryKeyField()
    uuid = models.CharField(max_length=36, unique=True, validators=[validate_uuid])
    secret_hash = models.CharField(max_length=200)
    environment_name = models.CharField(max_length=200, blank=True, null=True)
    service_name = models.CharField(max_length=200, blank=True, null=True)
    unit_name = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, blank=True, null=True)
    ssh_public_key = models.CharField(max_length=2048)
    auth = models.ForeignKey(Auth, validators=[validate_machine_auth])
    storage = models.ForeignKey(Storage)
    active = models.BooleanField(default=True)
    date_registered = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.unit_name, self.uuid)


class Source(models.Model):
    id = UuidPrimaryKeyField()
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


add_introspection_rules([], ["^turku_api\.models\.UuidPrimaryKeyField"])
