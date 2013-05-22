# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Asset'
        db.create_table('assets_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slot_duration', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('capacity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('max_bookable_slots', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('assets', ['Asset'])


    def backwards(self, orm):
        # Deleting model 'Asset'
        db.delete_table('assets_asset')


    models = {
        'assets.asset': {
            'Meta': {'object_name': 'Asset'},
            'capacity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_bookable_slots': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slot_duration': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        }
    }

    complete_apps = ['assets']