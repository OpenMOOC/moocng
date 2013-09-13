# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExternalApp'
        db.create_table('externalapps_externalapp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('base_url', self.gf('django.db.models.fields.TextField')()),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
        ))
        db.send_create_signal('externalapps', ['ExternalApp'])


    def backwards(self, orm):
        # Deleting model 'ExternalApp'
        db.delete_table('externalapps_externalapp')


    models = {
        'externalapps.externalapp': {
            'Meta': {'object_name': 'ExternalApp'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'base_url': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'})
        }
    }

    complete_apps = ['externalapps']