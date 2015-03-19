# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Source.bwlimit'
        db.add_column(u'turku_api_source', 'bwlimit',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Source.bwlimit'
        db.delete_column(u'turku_api_source', 'bwlimit')


    models = {
        u'turku_api.auth': {
            'Meta': {'unique_together': "(('secret', 'secret_type'),)", 'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'680a3f5a-deab-4317-9fd9-d0b58142b8b2'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.backuplog': {
            'Meta': {'object_name': 'BackupLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'aeb01acd-3618-4d02-af8c-ff1d6e66bb67'", 'max_length': '36', 'primary_key': 'True'}),
            'snapshot': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Storage']", 'null': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'turku_api.filterset': {
            'Meta': {'object_name': 'FilterSet'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'filters': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'4955d972-e60b-4441-a895-141846550e6c'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'0bed746a-f4ae-4131-a7fc-27ff2a900f1e'", 'max_length': '36', 'primary_key': 'True'}),
            'secret_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ssh_public_key': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Storage']"}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'})
        },
        u'turku_api.source': {
            'Meta': {'unique_together': "(('machine', 'name'),)", 'object_name': 'Source'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bwlimit': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_last_backed_up': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_next_backup': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exclude': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'filter': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '200'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'3bb34730-197d-4a2e-a811-d1302a7daa10'", 'max_length': '36', 'primary_key': 'True'}),
            'large_modifying_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'large_rotating_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Machine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'retention': ('django.db.models.fields.CharField', [], {'default': "'last 5 days, earliest of month'", 'max_length': '200'}),
            'shared_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snapshot_mode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'turku_api.storage': {
            'Meta': {'object_name': 'Storage'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Auth']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_checked_in': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'03ccbf95-0de7-47b2-b25c-6f4c5460fce6'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'space_available': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'space_total': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ssh_ping_host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host_keys': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '65536'}),
            'ssh_ping_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ssh_ping_user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['turku_api']