# -*- coding: utf-8 -*-
# Copyright 2013 Pablo Martín
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


import os

from shutil import copyfile

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.datastructures import SortedDict
from deep_serializer import BaseMetaWalkClass, WALKING_STOP, ONLY_REFERENCE, WALKING_INTO_CLASS
from deep_serializer.exceptions import update_the_serializer
from moocng.slug import unique_slugify


class TraceCourseId(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        if not hasattr(initial_obj, 'trace_natural_keys'):
            initial_obj.trace_natural_keys = {}
        model_name = obj.__class__.__name__
        if not model_name in initial_obj.trace_natural_keys:
            initial_obj.trace_natural_keys[model_name] = {}
        initial_obj.trace_natural_keys[model_name][obj.natural_key()] = obj.pk
        return obj

    @classmethod
    def pre_save(cls, initial_obj, obj, request=None):
        super(TraceCourseId, cls).pre_save(initial_obj, obj, request=request)
        if not hasattr(initial_obj, 'trace_ids'):
            initial_obj.trace_ids = SortedDict({})
            initial_obj.slug_original = initial_obj.__class__.objects.get(pk=initial_obj.pk).slug
        model_name = obj.__class__.__name__
        if not model_name in initial_obj.trace_ids:
            initial_obj.trace_ids[model_name] = {}

    @classmethod
    def post_save(cls, initial_obj, obj, request=None):
        super(TraceCourseId, cls).post_save(initial_obj, obj, request=request)
        model_name = obj.__class__.__name__
        obj_old_id = initial_obj.trace_natural_keys[model_name][obj.natural_key()]
        initial_obj.trace_ids[model_name][obj_old_id] = obj.pk


class CourseClone(TraceCourseId):

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name in ('students', 'teachers', 'courses_created_of'):
            return WALKING_STOP
        elif field_name in ('owner', 'completion_badge', 'created_from'):
            return ONLY_REFERENCE
        elif field_name == 'unit':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.name = obj.name + ' (Copy)'
        obj.status = 'd'
        obj.created_from_id = initial_obj.pk
        unique_slugify(obj, obj.slug, exclude_instance=False)
        obj = super(CourseClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def post_save(cls, initial_obj, obj, request=None):
        super(CourseClone, cls).post_save(initial_obj, obj, request=request)
        # Save the teachers
        course_teachers = initial_obj.courseteacher_set.all()
        CourseTeacher = initial_obj.courseteacher_set.model
        primary_key_field = CourseTeacher._meta.pk
        course_field = CourseTeacher._meta.get_field('course')
        for course_teacher in course_teachers:
            fields = {}
            for field in course_teacher._meta.fields:
                if field == primary_key_field:
                    continue
                elif field == course_field:
                    fields[field.name] = obj
                else:
                    fields[field.name] = getattr(course_teacher, field.name)
            CourseTeacher.objects.create(**fields)


class UnitClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.course = initial_obj
        obj = super(UnitClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'course':
            return WALKING_STOP
        elif field_name == 'knowledgequantum':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)


class KnowledgeQuantumClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.unit.course = initial_obj
        obj = super(KnowledgeQuantumClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'unit':
            return ONLY_REFERENCE
        elif field_name in ('attachment', 'question', 'peerreviewassignment'):
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)


class QuestionClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.kq.unit.course = initial_obj
        obj = super(QuestionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'kq':
            return ONLY_REFERENCE
        elif field_name == 'option':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)


class OptionClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.question.kq.unit.course = initial_obj
        obj = super(OptionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'question':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)


class AttachmentClone(TraceCourseId):

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'kq':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.kq.unit.course = initial_obj
        storage = get_storage_class()()
        attachment_name = storage.get_available_name(obj.attachment.name)
        if not hasattr(initial_obj, 'attachments'):
            initial_obj.attachments = {}
        attachment_path = os.path.join(settings.MEDIA_ROOT, attachment_name)
        initial_obj.attachments[attachment_path] = obj.attachment.path
        obj.attachment.name = attachment_name
        obj = super(AttachmentClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def post_save(cls, initial_obj, obj, request=None):
        super(AttachmentClone, cls).post_save(initial_obj, obj, request=request)
        new_path = obj.attachment.path
        old_path = initial_obj.attachments[new_path]
        if os.path.exists(old_path) or not settings.DEBUG:
            copyfile(old_path, new_path)


class PeerReviewAssignmentClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.kq.unit.course = initial_obj
        obj = super(PeerReviewAssignmentClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'kq':
            return ONLY_REFERENCE
        elif field_name == 'criteria':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)


class EvaluationCriterionClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj.assignment.kq.unit.course = initial_obj
        obj = super(EvaluationCriterionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'assignment':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)
