# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organization'
        db.create_table('profile_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=256)),
        ))
        db.send_create_signal('profile', ['Organization'])

        # Deleting field 'UserProfile.organization'
        db.delete_column('profile_userprofile', 'organization')

        # Adding M2M table for field organization on 'UserProfile'
        db.create_table('profile_userprofile_organization', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['profile.userprofile'], null=False)),
            ('organization', models.ForeignKey(orm['profile.organization'], null=False))
        ))
        db.create_unique('profile_userprofile_organization', ['userprofile_id', 'organization_id'])


    def backwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table('profile_organization')

        # Adding field 'UserProfile.organization'
        db.add_column('profile_userprofile', 'organization',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field organization on 'UserProfile'
        db.delete_table('profile_userprofile_organization')


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
        'courses.announcement': {
            'Meta': {'ordering': "('-datetime',)", 'object_name': 'Announcement'},
            'content': ('tinymce.models.HTMLField', [], {}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']", 'null': 'True', 'blank': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'courses.course': {
            'Meta': {'ordering': "['order']", 'object_name': 'Course'},
            'background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certification_alt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'certification_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'certification_banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'completion_badge': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'course'", 'null': 'True', 'to': "orm['badges.Badge']"}),
            'created_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'courses_created_of'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['courses.Course']"}),
            'description': ('tinymce.models.HTMLField', [], {}),
            'ects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'enrollment_method': ('django.db.models.fields.CharField', [], {'default': "'free'", 'max_length': '200'}),
            'estimated_effort': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_audience': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'is_activity_clonable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses_as_language'", 'symmetrical': 'False', 'through': "orm['courses.CourseLanguage']", 'to': "orm['courses.Language']"}),
            'learning_goals': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'max_mass_emails_month': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'max_reservations_pending': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'max_reservations_total': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '8'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses_as_owner'", 'to': "orm['auth.User']"}),
            'promotion_media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'promotion_media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'requirements': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
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
        'courses.courselanguage': {
            'Meta': {'object_name': 'CourseLanguage'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Language']"})
        },
        'courses.coursestudent': {
            'Meta': {'object_name': 'CourseStudent'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_course_status': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '1'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'courses.staticpage': {
            'Meta': {'object_name': 'StaticPage'},
            'body': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'profile.organization': {
            'Meta': {'object_name': 'Organization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'profile.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_announcement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Announcement']", 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profile.Organization']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['profile']