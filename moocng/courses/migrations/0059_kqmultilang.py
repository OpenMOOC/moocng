# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Question.solution_text_en'
        db.add_column('courses_question', 'solution_text_en',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.solution_text_es'
        db.add_column('courses_question', 'solution_text_es',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.solution_text_it'
        db.add_column('courses_question', 'solution_text_it',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.solution_text_pt'
        db.add_column('courses_question', 'solution_text_pt',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.solution_text_fr'
        db.add_column('courses_question', 'solution_text_fr',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.solution_text_de'
        db.add_column('courses_question', 'solution_text_de',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_en'
        db.add_column('courses_option', 'solution_en',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_es'
        db.add_column('courses_option', 'solution_es',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_it'
        db.add_column('courses_option', 'solution_it',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_pt'
        db.add_column('courses_option', 'solution_pt',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_fr'
        db.add_column('courses_option', 'solution_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.solution_de'
        db.add_column('courses_option', 'solution_de',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_en'
        db.add_column('courses_option', 'text_en',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_es'
        db.add_column('courses_option', 'text_es',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_it'
        db.add_column('courses_option', 'text_it',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_pt'
        db.add_column('courses_option', 'text_pt',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_fr'
        db.add_column('courses_option', 'text_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.text_de'
        db.add_column('courses_option', 'text_de',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_en'
        db.add_column('courses_option', 'feedback_en',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_es'
        db.add_column('courses_option', 'feedback_es',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_it'
        db.add_column('courses_option', 'feedback_it',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_pt'
        db.add_column('courses_option', 'feedback_pt',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_fr'
        db.add_column('courses_option', 'feedback_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Option.feedback_de'
        db.add_column('courses_option', 'feedback_de',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_en'
        db.add_column('courses_knowledgequantum', 'title_en',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_es'
        db.add_column('courses_knowledgequantum', 'title_es',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_it'
        db.add_column('courses_knowledgequantum', 'title_it',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_pt'
        db.add_column('courses_knowledgequantum', 'title_pt',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_fr'
        db.add_column('courses_knowledgequantum', 'title_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.title_de'
        db.add_column('courses_knowledgequantum', 'title_de',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_en'
        db.add_column('courses_knowledgequantum', 'teacher_comments_en',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_es'
        db.add_column('courses_knowledgequantum', 'teacher_comments_es',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_it'
        db.add_column('courses_knowledgequantum', 'teacher_comments_it',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_pt'
        db.add_column('courses_knowledgequantum', 'teacher_comments_pt',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_fr'
        db.add_column('courses_knowledgequantum', 'teacher_comments_fr',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.teacher_comments_de'
        db.add_column('courses_knowledgequantum', 'teacher_comments_de',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_en'
        db.add_column('courses_knowledgequantum', 'supplementary_material_en',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_es'
        db.add_column('courses_knowledgequantum', 'supplementary_material_es',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_it'
        db.add_column('courses_knowledgequantum', 'supplementary_material_it',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_pt'
        db.add_column('courses_knowledgequantum', 'supplementary_material_pt',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_fr'
        db.add_column('courses_knowledgequantum', 'supplementary_material_fr',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'KnowledgeQuantum.supplementary_material_de'
        db.add_column('courses_knowledgequantum', 'supplementary_material_de',
                      self.gf('tinymce.models.HTMLField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Question.solution_text_en'
        db.delete_column('courses_question', 'solution_text_en')

        # Deleting field 'Question.solution_text_es'
        db.delete_column('courses_question', 'solution_text_es')

        # Deleting field 'Question.solution_text_it'
        db.delete_column('courses_question', 'solution_text_it')

        # Deleting field 'Question.solution_text_pt'
        db.delete_column('courses_question', 'solution_text_pt')

        # Deleting field 'Question.solution_text_fr'
        db.delete_column('courses_question', 'solution_text_fr')

        # Deleting field 'Question.solution_text_de'
        db.delete_column('courses_question', 'solution_text_de')

        # Deleting field 'Option.solution_en'
        db.delete_column('courses_option', 'solution_en')

        # Deleting field 'Option.solution_es'
        db.delete_column('courses_option', 'solution_es')

        # Deleting field 'Option.solution_it'
        db.delete_column('courses_option', 'solution_it')

        # Deleting field 'Option.solution_pt'
        db.delete_column('courses_option', 'solution_pt')

        # Deleting field 'Option.solution_fr'
        db.delete_column('courses_option', 'solution_fr')

        # Deleting field 'Option.solution_de'
        db.delete_column('courses_option', 'solution_de')

        # Deleting field 'Option.text_en'
        db.delete_column('courses_option', 'text_en')

        # Deleting field 'Option.text_es'
        db.delete_column('courses_option', 'text_es')

        # Deleting field 'Option.text_it'
        db.delete_column('courses_option', 'text_it')

        # Deleting field 'Option.text_pt'
        db.delete_column('courses_option', 'text_pt')

        # Deleting field 'Option.text_fr'
        db.delete_column('courses_option', 'text_fr')

        # Deleting field 'Option.text_de'
        db.delete_column('courses_option', 'text_de')

        # Deleting field 'Option.feedback_en'
        db.delete_column('courses_option', 'feedback_en')

        # Deleting field 'Option.feedback_es'
        db.delete_column('courses_option', 'feedback_es')

        # Deleting field 'Option.feedback_it'
        db.delete_column('courses_option', 'feedback_it')

        # Deleting field 'Option.feedback_pt'
        db.delete_column('courses_option', 'feedback_pt')

        # Deleting field 'Option.feedback_fr'
        db.delete_column('courses_option', 'feedback_fr')

        # Deleting field 'Option.feedback_de'
        db.delete_column('courses_option', 'feedback_de')

        # Deleting field 'KnowledgeQuantum.title_en'
        db.delete_column('courses_knowledgequantum', 'title_en')

        # Deleting field 'KnowledgeQuantum.title_es'
        db.delete_column('courses_knowledgequantum', 'title_es')

        # Deleting field 'KnowledgeQuantum.title_it'
        db.delete_column('courses_knowledgequantum', 'title_it')

        # Deleting field 'KnowledgeQuantum.title_pt'
        db.delete_column('courses_knowledgequantum', 'title_pt')

        # Deleting field 'KnowledgeQuantum.title_fr'
        db.delete_column('courses_knowledgequantum', 'title_fr')

        # Deleting field 'KnowledgeQuantum.title_de'
        db.delete_column('courses_knowledgequantum', 'title_de')

        # Deleting field 'KnowledgeQuantum.teacher_comments_en'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_en')

        # Deleting field 'KnowledgeQuantum.teacher_comments_es'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_es')

        # Deleting field 'KnowledgeQuantum.teacher_comments_it'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_it')

        # Deleting field 'KnowledgeQuantum.teacher_comments_pt'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_pt')

        # Deleting field 'KnowledgeQuantum.teacher_comments_fr'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_fr')

        # Deleting field 'KnowledgeQuantum.teacher_comments_de'
        db.delete_column('courses_knowledgequantum', 'teacher_comments_de')

        # Deleting field 'KnowledgeQuantum.supplementary_material_en'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_en')

        # Deleting field 'KnowledgeQuantum.supplementary_material_es'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_es')

        # Deleting field 'KnowledgeQuantum.supplementary_material_it'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_it')

        # Deleting field 'KnowledgeQuantum.supplementary_material_pt'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_pt')

        # Deleting field 'KnowledgeQuantum.supplementary_material_fr'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_fr')

        # Deleting field 'KnowledgeQuantum.supplementary_material_de'
        db.delete_column('courses_knowledgequantum', 'supplementary_material_de')


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
        'courses.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kq': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.KnowledgeQuantum']"})
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
        'courses.knowledgequantum': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('title', 'unit'),)", 'object_name': 'KnowledgeQuantum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'supplementary_material': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'supplementary_material_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_material_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_material_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_material_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_material_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'supplementary_material_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'teacher_comments_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'teacher_comments_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_pt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'unit': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Unit']"}),
            'weight': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'courses.language': {
            'Meta': {'object_name': 'Language'},
            'abbr': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'courses.option': {
            'Meta': {'unique_together': "(('question', 'x', 'y'),)", 'object_name': 'Option'},
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'feedback_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'feedback_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'feedback_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'feedback_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'feedback_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'feedback_pt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'optiontype': ('django.db.models.fields.CharField', [], {'default': "'t'", 'max_length': '1'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Question']"}),
            'solution': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'solution_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'solution_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'solution_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'solution_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'solution_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'solution_pt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_de': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_es': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_fr': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_it': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'text_pt': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '100'}),
            'x': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'y': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'courses.question': {
            'Meta': {'object_name': 'Question'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kq': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.KnowledgeQuantum']", 'unique': 'True'}),
            'last_frame': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'solution_media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'solution_media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'solution_text': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'solution_text_de': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'solution_text_en': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'solution_text_es': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'solution_text_fr': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'solution_text_it': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'solution_text_pt': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'use_last_frame': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
        },
        'courses.transcription': {
            'Meta': {'object_name': 'Transcription'},
            'filename': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kq': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.KnowledgeQuantum']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Language']"}),
            'transcription_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'courses.unit': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('title', 'course'),)", 'object_name': 'Unit'},
            'course': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Course']"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_pt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'unittype': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'weight': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['courses']