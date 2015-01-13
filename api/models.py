from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
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


class Machine(models.Model):
    machine_uuid = models.CharField(max_length=36, primary_key=True, db_column='id', validators=[validate_uuid])
    machine_secret = models.CharField(max_length=200)
    environment_name = models.CharField(max_length=200, blank=True, null=True)
    service_name = models.CharField(max_length=200, blank=True, null=True)
    unit_name = models.CharField(max_length=200)
    ssh_public_key = models.CharField(max_length=2048)
    date_registered = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(default=datetime.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.unit_name, self.machine_uuid)


class Source(models.Model):
    source_uuid = models.CharField(max_length=36, primary_key=True, db_column='id', default=new_uuid, validators=[validate_uuid])
    name = models.CharField(max_length=200)
    machine = models.ForeignKey(Machine)
    comment = models.CharField(max_length=200, blank=True, null=True)
    path = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    exclude = models.CharField(max_length=2048, default='[]', validators=[validate_json_string_list])
    frequency = models.CharField(max_length=200, default='daily')
    shared_service = models.BooleanField(default=False)
    snapshot = models.BooleanField(default=False)
    inplace = models.BooleanField(default=False)
    date_registered = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(default=datetime.now)
    date_checked_in = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = (('machine', 'name'),)

    def __unicode__(self):
        return '%s %s' % (self.machine.unit_name, self.path)
