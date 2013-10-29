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
    def pre_save(cls, initial_obj, obj, request=None):
        super(TraceCourseId, cls).pre_save(initial_obj, obj, request=request)
        if not hasattr(initial_obj, 'trace_ids'):
            initial_obj.trace_ids = SortedDict({})
            initial_obj.slug_original = initial_obj.__class__.objects.get(pk=initial_obj.pk).slug
        model_name = obj.__class__.__name__
        if not model_name in initial_obj.trace_ids:
            initial_obj.trace_ids[model_name] = {}
        natural_original_key = (initial_obj.slug_original,) + obj.natural_key()[1:]
        initial_obj.last_id = obj.__class__.objects.get_by_natural_key(*natural_original_key).pk

    @classmethod
    def post_save(cls, initial_obj, obj, request=None):
        super(TraceCourseId, cls).post_save(initial_obj, obj, request=request)
        model_name = obj.__class__.__name__
        initial_obj.trace_ids[model_name][initial_obj.last_id] = obj.pk
        initial_obj.last_id = None


class CourseClone(TraceCourseId):

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name in ('students',):
            return WALKING_STOP
        elif field_name == 'teachers':
            obj._meta.get_field(field_name).rel.through._meta.auto_created = True
            return ONLY_REFERENCE
        elif field_name in ('owner', 'completion_badge'):
            return ONLY_REFERENCE
        elif field_name == 'unit':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj = super(CourseClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.name = obj.name + ' (Copy)'
        unique_slugify(obj, obj.slug, exclude_instance=False)
        return obj


class UnitClone(TraceCourseId):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj = super(UnitClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.course = initial_obj
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
        obj = super(KnowledgeQuantumClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.unit.course = initial_obj
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
        obj = super(QuestionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.kq.unit.course = initial_obj
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
        obj = super(OptionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.question.kq.unit.course = initial_obj
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'question':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)


class AttachmentClone(BaseMetaWalkClass):

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'kq':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj = super(AttachmentClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        storage = get_storage_class()()
        attachment_name = storage.get_available_name(obj.attachment.name)
        if not hasattr(initial_obj, 'attachments'):
            initial_obj.attachments = {}
        attachment_path = os.path.join(settings.MEDIA_ROOT, attachment_name)
        initial_obj.attachments[attachment_path] = obj.attachment.path
        obj.attachment.name = attachment_name
        return obj

    @classmethod
    def post_save(cls, initial_obj, obj, request=None):
        super(AttachmentClone, cls).post_save(initial_obj, obj, request=request)
        new_path = obj.attachment.path
        old_path = initial_obj.attachments[new_path]
        if os.path.exists(old_path) and settings.DEBUG:
            copyfile(old_path, new_path)


class PeerReviewAssignmentClone(BaseMetaWalkClass):

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'kq':
            return ONLY_REFERENCE
        elif field_name == 'criteria':
            return WALKING_INTO_CLASS
        update_the_serializer(obj, field_name)


class EvaluationCriterionClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request=None, serialize_options=None):
        obj = super(EvaluationCriterionClone, cls).pre_serialize(initial_obj, obj, request, serialize_options=serialize_options)
        obj.assignment.kq.unit.course = initial_obj
        return obj

    @classmethod
    def walking_into_class(cls, initial_obj, obj, field_name, model, request=None):
        if field_name == 'assignment':
            return ONLY_REFERENCE
        update_the_serializer(obj, field_name)
