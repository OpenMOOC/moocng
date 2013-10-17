# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Issuer.url'
        db.alter_column('badges_issuer', 'url', self.gf('django.db.models.fields.URLField')(max_length=255))

        # Changing field 'Badge.criteria'
        db.alter_column('badges_badge', 'criteria', self.gf('django.db.models.fields.URLField')(max_length=255))
        # Deleting field 'Award.image'
        db.delete_column('badges_award', 'image')

        # Adding field 'Award.identity_type'
        db.add_column('badges_award', 'identity_type',
                      self.gf('django.db.models.fields.CharField')(default='email', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Award.identity_hash'
        db.add_column('badges_award', 'identity_hash',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Award.identity_hashed'
        db.add_column('badges_award', 'identity_hashed',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Award.identity_salt'
        db.add_column('badges_award', 'identity_salt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Issuer.url'
        db.alter_column('badges_issuer', 'url', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Badge.criteria'
        db.alter_column('badges_badge', 'criteria', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding field 'Award.image'
        db.add_column('badges_award', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Award.identity_type'
        db.delete_column('badges_award', 'identity_type')

        # Deleting field 'Award.identity_hash'
        db.delete_column('badges_award', 'identity_hash')

        # Deleting field 'Award.identity_hashed'
        db.delete_column('badges_award', 'identity_hashed')

        # Deleting field 'Award.identity_salt'
        db.delete_column('badges_award', 'identity_salt')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'badges.alignment': {
            'Meta': {'object_name': 'Alignment'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'badges.award': {
            'Meta': {'ordering': "['-modified', '-awarded']", 'unique_together': "(('user', 'badge'),)", 'object_name': 'Award'},
            'awarded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'awards_set'", 'to': "orm['badges.Badge']"}),
            'evidence': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity_hash': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'identity_hashed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'identity_salt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'identity_type': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_awards'", 'to': "orm['auth.User']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'2475def2-366a-11e3-9eec-ac81126ee5f9'", 'max_length': '255', 'db_index': 'True'})
        },
        'badges.badge': {
            'Meta': {'ordering': "['-modified', '-created']", 'object_name': 'Badge'},
            'alignments': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'alignments'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['badges.Alignment']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'tags'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['badges.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'badges.identity': {
            'Meta': {'object_name': 'Identity'},
            'hashed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity_hash': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'identity'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'badges.issuer': {
            'Meta': {'object_name': 'Issuer'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'badges.revocation': {
            'Meta': {'object_name': 'Revocation'},
            'award': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revocations'", 'to': "orm['badges.Award']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'badges.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['badges']