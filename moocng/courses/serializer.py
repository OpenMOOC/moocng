import os

from shutil import copyfile

from django.conf import settings
from django.core.files.storage import get_storage_class
from deep_serialize import BaseMetaWalkClass, WALKING_STOP, ONLY_REFERENCE, WALKING_INTO_CLASS
from moocng.slug import unique_slugify


class CourseClone(BaseMetaWalkClass):

    @classmethod
    def walking_into_class(cls, obj, field_name, model):
        if field_name == 'teachers':
            obj._meta.get_field(field_name).rel.through._meta.auto_created = True
            return ONLY_REFERENCE
        elif field_name in ('owner', 'completion_badge'):
            return ONLY_REFERENCE
        elif field_name in ('students',):
            return WALKING_STOP
        return WALKING_INTO_CLASS

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(CourseClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.name = obj.name + ' (Copy)'
        unique_slugify(obj, obj.slug, exclude_instance=False)
        return obj


class UnitClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(UnitClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.course = initial_obj
        return obj


class KnowledgeQuantumClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(KnowledgeQuantumClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.unit.course = initial_obj
        return obj


class QuestionClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(QuestionClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.kq.unit.course = initial_obj
        return obj


class OptionClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(OptionClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.question.kq.unit.course = initial_obj
        return obj


class AttachmentClone(QuestionClone):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(AttachmentClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        storage = get_storage_class()()
        attachment_name = storage.get_available_name(obj.attachment.name)
        if not hasattr(initial_obj, 'attachments'):
            initial_obj.attachments = {}
        attachment_path = os.path.join(settings.MEDIA_ROOT, attachment_name)
        initial_obj.attachments[attachment_path] = obj.attachment.path
        obj.attachment.name = attachment_name
        return obj

    @classmethod
    def post_save(cls, initial_obj, obj):
        super(AttachmentClone, cls).post_save(initial_obj, obj)
        new_path = obj.attachment.path
        old_path = initial_obj.attachments[new_path]
        if os.path.exists(old_path) and settings.DEBUG:
            copyfile(old_path, new_path)


class PeerReviewAssignmentClone(QuestionClone):
    pass


class EvaluationCriterionClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(EvaluationCriterionClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.assignment.kq.unit.course = initial_obj
        return obj
