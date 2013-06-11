# -*- coding: utf-8 -*-
# Copyright 2013 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bson import Code
from south.v2 import DataMigration
import pymongo
from pymongo.errors import OperationFailure

from django.utils import simplejson

from moocng.mongodb import get_db


class Migration(DataMigration):

    def forwards(self, orm):
        question_course = {}
        question_unit = {}
        question_kq = {}

        for course in orm['courses.course'].objects.all():
            for unit in course.unit_set.all():
                for kq in unit.knowledgequantum_set.all():
                    try:
                        question = kq.question_set.get()
                    except kq.question_set.model.DoesNotExist:
                        continue
                    question_course[str(question.id)] = course.id
                    question_unit[str(question.id)] = unit.id
                    question_kq[str(question.id)] = kq.id

        js_migration = """
var question_course = %s,
    question_unit = %s,
    question_kq = %s;

db.answers_new.drop();

db.answers.find().forEach(function (answer) {
    var replyList,
        question,
        question_id;
    for (question_id in answer.questions) {
        replyList = [];
        question = answer.questions[question_id];
        question.replyList.forEach(function (reply) {
            replyList.push({
                option: parseInt(reply.option, 10),
                value: reply.value
            });
        });
        db.answers_new.insert({
            user_id: parseInt(answer.user, 10),
            question_id: parseInt(question_id, 10),
            course_id: question_course[question_id],
            unit_id: question_unit[question_id],
            kq_id: question_kq[question_id],
            replyList: replyList,
            date: ISODate(question.date)
        });
    }
});
        """ % (simplejson.dumps(question_course),
               simplejson.dumps(question_unit),
               simplejson.dumps(question_kq))

        connector = get_db()
        db = connector.get_database()
        db.eval(Code(js_migration))

        db.answers.drop()
        try:
            db.answers_new.rename('answers')
        except OperationFailure:
            # if the answers collection was empty, then there is no new
            # collection to rename, but that is okay
            pass

        print "Answers collection migrated, old collection dropped. Creating indexes..."

        db.answers.create_index([("user_id", pymongo.ASCENDING),
                                 ("question_id", pymongo.ASCENDING)])
        db.answers.create_index([("question_id", pymongo.ASCENDING)])

    def backwards(self, orm):
        "Write your backwards methods here."
        # TODO
        raise RuntimeError("Cannot reverse this migration.")

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
        'badges.badge': {
            'Meta': {'ordering': "['-modified', '-created']", 'object_name': 'Badge'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'courses.announcement': {
            'Meta': {'object_name': 'Announcement'},
            'content': ('tinymce.models.HTMLField', [], {}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'courses.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kq': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.KnowledgeQuantum']"})
        },
        'courses.course': {
            'Meta': {'ordering': "['order']", 'object_name': 'Course'},
            'certification_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'certification_banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'completion_badge': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'course'", 'unique': 'True', 'null': 'True', 'to': "orm['badges.Badge']"}),
            'description': ('tinymce.models.HTMLField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'enrollment_method': ('django.db.models.fields.CharField', [], {'default': "'free'", 'max_length': '200'}),
            'estimated_effort': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_audience': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'learning_goals': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses_as_owner'", 'to': "orm['auth.User']"}),
            'promotion_media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'promotion_media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'requirements': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '10'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses_as_student'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses_as_teacher'", 'symmetrical': 'False', 'through': "orm['courses.CourseTeacher']", 'to': "orm['auth.User']"}),
            'threshold': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'})
        },
        'courses.courseteacher': {
            'Meta': {'ordering': "['order']", 'object_name': 'CourseTeacher'},
            'course': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'courses.knowledgequantum': {
            'Meta': {'ordering': "['order']", 'object_name': 'KnowledgeQuantum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_content_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'media_content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'supplementary_material': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'teacher_comments': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Unit']"}),
            'weight': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'courses.option': {
            'Meta': {'object_name': 'Option'},
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optiontype': ('django.db.models.fields.CharField', [], {'default': "'t'", 'max_length': '1'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Question']"}),
            'solution': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
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
            'use_last_frame': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'courses.unit': {
            'Meta': {'ordering': "['order']", 'object_name': 'Unit'},
            'course': ('adminsortable.fields.SortableForeignKey', [], {'to': "orm['courses.Course']"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unittype': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'weight': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['courses']
    symmetrical = True
