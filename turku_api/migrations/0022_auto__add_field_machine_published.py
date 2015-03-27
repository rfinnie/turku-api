# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Machine.published'
        db.add_column(u'turku_api_machine', 'published',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Machine.published'
        db.delete_column(u'turku_api_machine', 'published')


    models = {
        u'turku_api.auth': {
            'Meta': {'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'9a150708-0e44-4a53-b82a-56403e394af9'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.backuplog': {
            'Meta': {'object_name': 'BackupLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'2e67fc71-a2ee-434b-a0bd-5f77d93dc0b5'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'e31c84aa-ecfa-4165-a830-9e6296f83d2d'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'22e9553c-98ed-45c1-8a02-fc596e2eb32d'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'51db0d17-b49d-401e-a7cf-b91246893188'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'43a62b0c-470e-4f92-a7bc-794190433312'", 'max_length': '36', 'primary_key': 'True'}),
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
