# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Storage.published'
        db.add_column(u'turku_api_storage', 'published',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Storage.published'
        db.delete_column(u'turku_api_storage', 'published')


    models = {
        u'turku_api.auth': {
            'Meta': {'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'13ccc96c-1f0b-46ef-8f9f-bea4ed6a86be'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.backuplog': {
            'Meta': {'object_name': 'BackupLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'f1ec4035-8fd6-416a-b091-bf02c9e84bdc'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'42694e33-af54-482a-a98e-f2a30098f7c3'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'fd957c7e-7106-41d2-b3c9-eafb391c72b1'", 'max_length': '36', 'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'09b367b4-76fd-45e2-93f0-9883c4a5d88d'", 'max_length': '36', 'primary_key': 'True'}),
            'large_modifying_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'large_rotating_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Machine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'retention': ('django.db.models.fields.CharField', [], {'default': "'last 5 days, earliest of month'", 'max_length': '200'}),
            'shared_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snapshot_mode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'turku_api.storage': {
            'Meta': {'object_name': 'Storage'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Auth']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_checked_in': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'3fb039a5-6e7f-4f88-b763-d3da76046cc6'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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