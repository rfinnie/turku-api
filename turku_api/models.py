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

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import is_password_usable
from django.utils import timezone
from datetime import timedelta
from south.modelsinspector import add_introspection_rules
import json
import uuid


def new_uuid():
    return str(uuid.uuid4())


def validate_uuid(value):
    try:
        str(uuid.UUID(value))
    except ValueError:
        raise ValidationError('Invalid UUID format')


def validate_hashed_password(value):
    if not is_password_usable(value):
        raise ValidationError('Invalid hashed password')


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
        kwargs['blank'] = True
        kwargs['default'] = new_uuid
        kwargs['editable'] = False
        kwargs['max_length'] = 36
        kwargs['primary_key'] = True
        super(UuidPrimaryKeyField, self).__init__(*args, **kwargs)


class Auth(models.Model):
    SECRET_TYPES = (
        ('machine_reg', 'Machine registration'),
        ('storage_reg', 'Storage registration'),
    )
    id = UuidPrimaryKeyField()
    name = models.CharField(
        max_length=200, unique=True,
        help_text='Human-readable name of this auth.',
    )
    secret_hash = models.CharField(
        max_length=200,
        validators=[validate_hashed_password],
        help_text='Hashed secret (password) of this auth.',
    )
    secret_type = models.CharField(
        max_length=200, choices=SECRET_TYPES,
        help_text='Auth secret type (machine/storage).',
    )
    comment = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Human-readable comment.',
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether this auth is enabled.  Disabling prevents new registrations using its key, and prevents ' +
                  'existing machines using its key from updating their configs.',
    )
    date_added = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this auth was added.',
    )

    def __unicode__(self):
        return self.name


class Storage(models.Model):
    def healthy(self):
        now = timezone.now()
        if now <= (self.date_registered + timedelta(minutes=30)):
            # New registration, assume it's healthy
            return True
        if not self.date_checked_in:
            return False
        return (now <= (self.date_checked_in + timedelta(minutes=30)))
    healthy.boolean = True

    id = UuidPrimaryKeyField()
    name = models.CharField(
        max_length=200, unique=True,
        help_text='Name of this storage unit.  This is used as its login ID and must be unique.',
    )
    secret_hash = models.CharField(
        max_length=200,
        validators=[validate_hashed_password],
        help_text='Hashed secret (password) of this storage unit.',
    )
    comment = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Human-readable comment.',
    )
    ssh_ping_host = models.CharField(
        max_length=200,
        verbose_name='SSH ping host',
        help_text='Hostname/IP address of this storage unit\'s SSH server.',
    )
    ssh_ping_host_keys = models.CharField(
        max_length=65536, default='[]',
        validators=[validate_json_string_list],
        verbose_name='SSH ping host keys',
        help_text='JSON list of this storage unit\'s SSH host keys.',
    )
    ssh_ping_port = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name='SSH ping port',
        help_text='Port number of this storage unit\'s SSH server.',
    )
    ssh_ping_user = models.CharField(
        max_length=200,
        verbose_name='SSH ping user',
        help_text='Username of this storage unit\'s SSH server.',
    )
    space_total = models.PositiveIntegerField(
        default=0,
        help_text='Total disk space of this storage unit\'s storage directories, in MiB.',
    )
    space_available = models.PositiveIntegerField(
        default=0,
        help_text='Available disk space of this storage unit\'s storage directories, in MiB.',
    )
    auth = models.ForeignKey(
        Auth, validators=[validate_storage_auth],
        help_text='Storage auth used to register this storage unit.',
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether this storage unit is enabled.  Disabling prevents this storage unit from checking in or ' +
                  'being assigned to new machines. Existing machines which ping this storage unit will get errors ' +
                  'because this storage unit can no longer query the API server.',
    )
    published = models.BooleanField(
        default=True,
        help_text='Whether this storage unit has been enabled by itself.',
    )
    date_registered = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this storage unit was registered.',
    )
    date_updated = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this storage unit presented a modified config.',
    )
    date_checked_in = models.DateTimeField(
        blank=True, null=True,
        help_text='Date/time this storage unit last checked in.',
    )

    def __unicode__(self):
        return self.name


class Machine(models.Model):
    def healthy(self):
        now = timezone.now()
        if now <= (self.date_registered + timedelta(hours=1)):
            # New registration, assume it's healthy
            return True
        if not self.date_checked_in:
            return False
        return (now <= (self.date_checked_in + timedelta(hours=4)))
    healthy.boolean = True

    id = UuidPrimaryKeyField()
    uuid = models.CharField(
        max_length=36, unique=True, validators=[validate_uuid],
        verbose_name='UUID',
        help_text='UUID of this machine.  This UUID is set by the machine and must be globally unique.',
    )
    secret_hash = models.CharField(
        max_length=200,
        validators=[validate_hashed_password],
        help_text='Hashed secret (password) of this machine.',
    )
    environment_name = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Environment this machine is part of.',
    )
    service_name = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Service this machine is part of.  For Juju units, this is the first part of the unit name ' +
                  '(before the slash).',
    )
    unit_name = models.CharField(
        max_length=200,
        help_text='Unit name of this machine.  For Juju units, this is the full unit name (e.g. "service-name/0").  ' +
                  'Otherwise, this should be the machine\'s hostname.',
    )
    comment = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Human-readable comment.',
    )
    ssh_public_key = models.CharField(
        max_length=2048,
        verbose_name='SSH public key',
        help_text='SSH public key of this machine\'s agent.',
    )
    auth = models.ForeignKey(
        Auth, validators=[validate_machine_auth],
        help_text='Machine auth used to register this machine.',
    )
    storage = models.ForeignKey(
        Storage,
        help_text='Storage unit this machine is assigned to.',
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether this machine is enabled.  Disabling removes its key from its storage unit, stops this ' +
                  'machine from updating its registration, etc.',
    )
    published = models.BooleanField(
        default=True,
        help_text='Whether this machine has been enabled by the machine agent.',
    )
    date_registered = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this machine was registered.',
    )
    date_updated = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this machine presented a modified config.',
    )
    date_checked_in = models.DateTimeField(
        blank=True, null=True,
        help_text='Date/time this machine last checked in.',
    )

    def __unicode__(self):
        return '%s (%s)' % (self.unit_name, self.uuid[0:8])


class Source(models.Model):
    def healthy(self):
        now = timezone.now()
        if now <= (self.date_added + timedelta(hours=4)):
            # New addition, assume it's healthy
            return True
        if not self.success:
            return False
        return (now <= (self.date_next_backup + timedelta(hours=10)))
    healthy.boolean = True

    SNAPSHOT_MODES = (
        ('none', 'No snapshotting'),
        ('attic', 'Attic'),
        ('link-dest', 'Hardlink trees (rsync --link-dest)'),
    )
    id = UuidPrimaryKeyField()
    name = models.CharField(
        max_length=200,
        help_text='Computer-readable source name identifier.',
    )
    machine = models.ForeignKey(
        Machine,
        help_text='Machine this source belongs to.',
    )
    comment = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Human-readable comment.',
    )
    path = models.CharField(
        max_length=200,
        help_text='Full filesystem path of this source.',
    )
    filter = models.CharField(
        max_length=2048, default='[]', validators=[validate_json_string_list],
        help_text='JSON list of rsync-compatible --filter options.',
    )
    exclude = models.CharField(
        max_length=2048, default='[]', validators=[validate_json_string_list],
        help_text='JSON list of rsync-compatible --exclude options.',
    )
    frequency = models.CharField(
        max_length=200, default='daily',
        help_text='How often to back up this source.',
    )
    retention = models.CharField(
        max_length=200, default='last 5 days, earliest of month',
        help_text='Retention schedule, describing when to preserve snapshots.',
    )
    bwlimit = models.CharField(
        max_length=200,
        blank=True, null=True,
        verbose_name='bandwidth limit',
        help_text='Bandwith limit for remote transfer, using the rsync --bwlimit format.',
    )
    snapshot_mode = models.CharField(
        blank=True, null=True,
        max_length=200, choices=SNAPSHOT_MODES,
        help_text='Override the storage unit\'s snapshot logic and use an explicit snapshot mode for this source.',
    )
    shared_service = models.BooleanField(
        default=False,
        help_text='Whether this source is part of a shared service of multiple machines to be backed up.',
    )
    large_rotating_files = models.BooleanField(
        default=False,
        help_text='Whether this source contains a number of large files which rotate through filenames, e.g. ' +
                  '"postgresql.1.dump.gz" becomes "postgresql.2.dump.gz".',
    )
    large_modifying_files = models.BooleanField(
        default=False,
        help_text='Whether this source contains a number of large files which grow or are otherwise modified, ' +
                  'e.g. log files or filesystem images.',
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether this source is enabled.  Disabling means the API server no longer gives it to the ' +
                  'storage unit, even if it\'s time for a backup.',
    )
    success = models.BooleanField(
        default=True,
        help_text='Whether this source\'s last backup was successful.',
    )
    published = models.BooleanField(
        default=True,
        help_text='Whether this source is actively being published by the machine agent.',
    )
    date_added = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this source was first added by the machine agent.',
    )
    date_updated = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time the machine presented a modified config of this source.',
    )
    date_last_backed_up = models.DateTimeField(
        blank=True, null=True,
        help_text='Date/time this source was last successfully backed up.',
    )
    date_next_backup = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this source is next scheduled to be backed up.  Set to now (or in the past) to ' +
                  'trigger a backup as soon as possible.',
    )

    class Meta:
        unique_together = (('machine', 'name'),)

    def __unicode__(self):
        return '%s %s' % (self.machine.unit_name, self.name)


class BackupLog(models.Model):
    id = UuidPrimaryKeyField()
    source = models.ForeignKey(
        Source,
        help_text='Source this log entry belongs to.',
    )
    date = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this log entry was received/processed.',
    )
    storage = models.ForeignKey(
        Storage, blank=True, null=True,
        help_text='Storage unit this backup occurred on.',
    )
    success = models.BooleanField(
        default=False,
        help_text='Whether this backup succeeded.',
    )
    date_begin = models.DateTimeField(
        blank=True, null=True,
        help_text='Date/time this backup began.',
    )
    date_end = models.DateTimeField(
        blank=True, null=True,
        help_text='Date/time this backup ended.',
    )
    snapshot = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Name of the created snapshot.',
    )
    summary = models.TextField(
        blank=True, null=True,
        help_text='Summary of the backup\'s events.',
    )

    def __unicode__(self):
        return '%s %s' % (str(self.source), self.date.strftime('%Y-%m-%d %H:%M:%S'))


class FilterSet(models.Model):
    id = UuidPrimaryKeyField()
    name = models.CharField(
        max_length=200, unique=True,
        help_text='Name of this filter set.',
    )
    filters = models.TextField(
        default='[]', validators=[validate_json_string_list],
        help_text='JSON list of this filter set\'s filter rules.',
    )
    comment = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Human-readable comment.',
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether this filter set is enabled.',
    )
    date_added = models.DateTimeField(
        default=timezone.now,
        help_text='Date/time this filter set was added.',
    )

    def __unicode__(self):
        return self.name


add_introspection_rules([], ["^turku_api\.models\.UuidPrimaryKeyField"])
