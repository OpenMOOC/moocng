# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BadgeByCourse.title_en'
        db.add_column('badges_badgebycourse', 'title_en',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.title_es'
        db.add_column('badges_badgebycourse', 'title_es',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.title_it'
        db.add_column('badges_badgebycourse', 'title_it',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.title_pt'
        db.add_column('badges_badgebycourse', 'title_pt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.title_fr'
        db.add_column('badges_badgebycourse', 'title_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.title_de'
        db.add_column('badges_badgebycourse', 'title_de',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_en'
        db.add_column('badges_badgebycourse', 'description_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_es'
        db.add_column('badges_badgebycourse', 'description_es',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_it'
        db.add_column('badges_badgebycourse', 'description_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_pt'
        db.add_column('badges_badgebycourse', 'description_pt',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_fr'
        db.add_column('badges_badgebycourse', 'description_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BadgeByCourse.description_de'
        db.add_column('badges_badgebycourse', 'description_de',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BadgeByCourse.title_en'
        db.delete_column('badges_badgebycourse', 'title_en')

        # Deleting field 'BadgeByCourse.title_es'
        db.delete_column('badges_badgebycourse', 'title_es')

        # Deleting field 'BadgeByCourse.title_it'
        db.delete_column('badges_badgebycourse', 'title_it')

        # Deleting field 'BadgeByCourse.title_pt'
        db.delete_column('badges_badgebycourse', 'title_pt')

        # Deleting field 'BadgeByCourse.title_fr'
        db.delete_column('badges_badgebycourse', 'title_fr')

        # Deleting field 'BadgeByCourse.title_de'
        db.delete_column('badges_badgebycourse', 'title_de')

        # Deleting field 'BadgeByCourse.description_en'
        db.delete_column('badges_badgebycourse', 'description_en')

        # Deleting field 'BadgeByCourse.description_es'
        db.delete_column('badges_badgebycourse', 'description_es')

        # Deleting field 'BadgeByCourse.description_it'
        db.delete_column('badges_badgebycourse', 'description_it')

        # Deleting field 'BadgeByCourse.description_pt'
        db.delete_column('badges_badgebycourse', 'description_pt')

        # Deleting field 'BadgeByCourse.description_fr'
        db.delete_column('badges_badgebycourse', 'description_fr')

        # Deleting field 'BadgeByCourse.description_de'
        db.delete_column('badges_badgebycourse', 'description_de')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '254'})
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
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'4d5a6e5e-c0cb-11e4-a589-08002759738a'", 'max_length': '255', 'db_index': 'True'})
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
        'badges.badgebycourse': {
            'Meta': {'object_name': 'BadgeByCourse'},
            'color': ('django.db.models.fields.TextField', [], {}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'criteria': ('django.db.models.fields.TextField', [], {}),
            'criteria_type': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_pt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_pt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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
        },
        'courses.course': {
            'Meta': {'ordering': "['order']", 'object_name': 'Course'},
            'background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certification_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'certification_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'completion_badge': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'course'", 'null': 'True', 'to': "orm['badges.Badge']"}),
            'created_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'courses_created_of'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['courses.Course']"}),
            'description': ('tinymce.models.HTMLField', [], {}),
            'description_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'description_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'description_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'description_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'ects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'enrollment_method': ('django.db.models.fields.CharField', [], {'default': "'free'", 'max_length': '200'}),
            'estimated_effort': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_de': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'estimated_effort_pt': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'external_certification_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'forum_slug': ('django.db.models.fields.CharField', [], {'max_length': '350', 'null': 'True', 'blank': 'True'}),
            'group_max_size': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '50'}),
            'has_groups': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hashtag': ('django.db.models.fields.CharField', [], {'default': "'Hashtag'", 'max_length': '128'}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_audience': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'is_activity_clonable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Language']", 'symmetrical': 'False'}),
            'learning_goals': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'learning_goals_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'max_mass_emails_month': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_pt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'official_course': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses_as_owner'", 'to': "orm['auth.User']"}),
            'promotion_media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'promotion_media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'requirements': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'requirements_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'requirements_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'requirements_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'requirements_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'requirements_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'requirements_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'static_page': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['courses.StaticPage']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '10'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses_as_student'", 'blank': 'True', 'through': "orm['courses.CourseStudent']", 'to': "orm['auth.User']"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses_as_teacher'", 'symmetrical': 'False', 'through': "orm['courses.CourseTeacher']", 'to': "orm['auth.User']"}),
            'threshold': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnail_alt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.coursestudent': {
            'Meta': {'object_name': 'CourseStudent'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_course_status': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '1'}),
            'pos_lat': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'pos_lon': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'courses.courseteacher': {
            'Meta': {'ordering': "['order']", 'object_name': 'CourseTeacher'},
            'course': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'courses.language': {
            'Meta': {'object_name': 'Language'},
            'abbr': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'courses.staticpage': {
            'Meta': {'object_name': 'StaticPage'},
            'body': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'body_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title_pt': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['badges']