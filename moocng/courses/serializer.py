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


class PeerReviewAssignmentClone(QuestionClone):
    pass


class EvaluationCriterionClone(BaseMetaWalkClass):

    @classmethod
    def pre_serialize(cls, initial_obj, obj, request, options=None):
        obj = super(EvaluationCriterionClone, cls).pre_serialize(initial_obj, obj, request, options=options)
        obj.assignment.kq.unit.course = initial_obj
        return obj
