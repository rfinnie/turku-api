# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Auth'
        db.create_table(u'turku_api_auth', (
            ('id', self.gf('django.db.models.fields.CharField')(default='e0e25ec6-3d61-4003-be88-0b8757a45f0e', max_length=36, primary_key=True)),
            ('secret', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('secret_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'turku_api', ['Auth'])

        # Adding model 'Storage'
        db.create_table(u'turku_api_storage', (
            ('id', self.gf('django.db.models.fields.CharField')(default='f3787734-5640-46d7-84ee-0ee6effa047d', max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('ssh_ping_host', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ssh_ping_host_keys', self.gf('django.db.models.fields.CharField')(default='[]', max_length=65536)),
            ('ssh_ping_port', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('ssh_ping_user', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('auth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turku_api.Auth'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_registered', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_checked_in', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'turku_api', ['Storage'])

        # Adding model 'Machine'
        db.create_table(u'turku_api_machine', (
            ('id', self.gf('django.db.models.fields.CharField')(default='3248bb6f-a6b5-4419-bf85-fb0a048e7669', max_length=36, primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('environment_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('unit_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('ssh_public_key', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('auth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turku_api.Auth'])),
            ('storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turku_api.Storage'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_registered', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_checked_in', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'turku_api', ['Machine'])

        # Adding model 'Source'
        db.create_table(u'turku_api_source', (
            ('id', self.gf('django.db.models.fields.CharField')(default='2a5243c2-f233-4764-9e6b-2fc302d69c34', max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('machine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turku_api.Machine'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('exclude', self.gf('django.db.models.fields.CharField')(default='[]', max_length=2048)),
            ('frequency', self.gf('django.db.models.fields.CharField')(default='daily', max_length=200)),
            ('retention', self.gf('django.db.models.fields.CharField')(default='last 5 days,earliest of month', max_length=200)),
            ('shared_service', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('large_rotating_files', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('large_modifying_files', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_last_backed_up', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_next_backup', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'turku_api', ['Source'])

        # Adding unique constraint on 'Source', fields ['machine', 'name']
        db.create_unique(u'turku_api_source', ['machine_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Source', fields ['machine', 'name']
        db.delete_unique(u'turku_api_source', ['machine_id', 'name'])

        # Deleting model 'Auth'
        db.delete_table(u'turku_api_auth')

        # Deleting model 'Storage'
        db.delete_table(u'turku_api_storage')

        # Deleting model 'Machine'
        db.delete_table(u'turku_api_machine')

        # Deleting model 'Source'
        db.delete_table(u'turku_api_source')


    models = {
        u'turku_api.auth': {
            'Meta': {'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'82469c17-def4-4a98-817f-e7a01b418a13'", 'max_length': '36', 'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.machine': {
            'Meta': {'object_name': 'Machine'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Auth']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_checked_in': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'environment_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'8f635288-8512-4e99-b1bb-c23dd1df2888'", 'max_length': '36', 'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ssh_public_key': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Storage']"}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'})
        },
        u'turku_api.source': {
            'Meta': {'unique_together': "(('machine', 'name'),)", 'object_name': 'Source'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_last_backed_up': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_next_backup': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exclude': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '200'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'d1310efd-e385-4b78-aa3a-84048417aa1a'", 'max_length': '36', 'primary_key': 'True'}),
            'large_modifying_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'large_rotating_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Machine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'retention': ('django.db.models.fields.CharField', [], {'default': "'last 5 days,earliest of month'", 'max_length': '200'}),
            'shared_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.storage': {
            'Meta': {'object_name': 'Storage'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Auth']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_checked_in': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'805c8ba4-b747-491c-a4f3-224c6cc82ce6'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host_keys': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '65536'}),
            'ssh_ping_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ssh_ping_user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['turku_api']