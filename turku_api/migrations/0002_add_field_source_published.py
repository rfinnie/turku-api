# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # https://code.djangoproject.com/ticket/22844
        db.delete_unique(u'turku_api_source', ['machine_id', 'name'])
        # Removing unique constraint on 'Source', fields ['machine', 'name']
        db.add_column(u'turku_api_source', 'published',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)
        # https://code.djangoproject.com/ticket/22844
        db.create_unique(u'turku_api_source', ['machine_id', 'name'])


    def backwards(self, orm):
        # https://code.djangoproject.com/ticket/22844
        db.delete_unique(u'turku_api_source', ['machine_id', 'name'])
        # Adding unique constraint on 'Source', fields ['machine', 'name']
        db.delete_column(u'turku_api_source', 'published')
        # https://code.djangoproject.com/ticket/22844
        db.create_unique(u'turku_api_source', ['machine_id', 'name'])


    models = {
        u'turku_api.auth': {
            'Meta': {'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'5f274f06-d657-434c-9b2d-67ad0e479b1c'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'279f55db-a4ff-4a00-a0bb-2fdbd908a5fd'", 'max_length': '36', 'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ssh_public_key': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Storage']"}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'})
        },
        u'turku_api.source': {
            'Meta': {'object_name': 'Source'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_last_backed_up': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_next_backup': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exclude': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '200'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'5472d78e-f55c-43a1-af17-4eb4d17144f4'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.CharField', [], {'default': "'3c920ee4-b744-41ca-bbb5-32aa7bea799f'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host_keys': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '65536'}),
            'ssh_ping_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ssh_ping_user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['turku_api']
