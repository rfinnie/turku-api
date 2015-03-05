# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FilterSet'
        db.create_table(u'turku_api_filterset', (
            ('id', self.gf('turku_api.models.UuidPrimaryKeyField')(default='a283d103-01a4-440d-a9b2-adb2e532e8b2', max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('filters', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'turku_api', ['FilterSet'])

        # Adding field 'Source.filter'
        db.add_column(u'turku_api_source', 'filter',
                      self.gf('django.db.models.fields.CharField')(default='[]', max_length=2048),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'FilterSet'
        db.delete_table(u'turku_api_filterset')

        # Deleting field 'Source.filter'
        db.delete_column(u'turku_api_source', 'filter')


    models = {
        u'turku_api.auth': {
            'Meta': {'unique_together': "(('secret', 'secret_type'),)", 'object_name': 'Auth'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'4966777d-84ef-46bb-8932-c5ab6337dc37'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'secret_type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'turku_api.backuplog': {
            'Meta': {'object_name': 'BackupLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'4de8a8a6-25f1-4c7f-bcc0-29cdab5bd517'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'7181cba9-6e58-4a8e-80d7-c5ba5d44eb2c'", 'max_length': '36', 'primary_key': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'1b8c26ec-1b8e-4281-8b49-ebfbc83ef94f'", 'max_length': '36', 'primary_key': 'True'}),
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
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_last_backed_up': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_next_backup': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exclude': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'filter': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '2048'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '200'}),
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'ac03635e-5835-4478-bc9f-35fdc8f766aa'", 'max_length': '36', 'primary_key': 'True'}),
            'large_modifying_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'large_rotating_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turku_api.Machine']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'retention': ('django.db.models.fields.CharField', [], {'default': "'last 5 days, earliest of month'", 'max_length': '200'}),
            'shared_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'id': ('turku_api.models.UuidPrimaryKeyField', [], {'default': "'a67da38d-db3e-467a-bec2-4792637a0b5e'", 'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'secret_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ssh_ping_host_keys': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '65536'}),
            'ssh_ping_port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ssh_ping_user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['turku_api']