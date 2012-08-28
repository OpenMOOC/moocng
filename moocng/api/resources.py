# -*- coding: utf-8 -*-
import re

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from moocng.api.authentication import DjangoAuthentication
from moocng.api.mongodb import get_db, get_user, MongoObj, MongoResource
from moocng.courses.models import (Unit, KnowledgeQuantum, Question, Option,
                                   Attachment)
from moocng.courses.utils import extract_YT_video_id


class UnitResource(ModelResource):

    class Meta:
        queryset = Unit.objects.all()
        resource_name = 'unit'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()


class KnowledgeQuantumResource(ModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.RelatedField('moocng.api.resources.QuestionResource',
                                   'question_set')
    videoID = fields.CharField(readonly=True)
    correct = fields.BooleanField()
    completed = fields.BooleanField()

    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'kq'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "unit": ('exact'),
        }

    def dispatch(self, request_type, request, **kwargs):
        db = get_db()
        self.user_answers = get_user(request, db.get_collection('answers'))
        self.user_activity = get_user(request, db.get_collection('activity'))
        return super(KnowledgeQuantumResource, self).dispatch(request_type,
                                                              request,
                                                              **kwargs)

    def dehydrate_question(self, bundle):
        question = bundle.data['question']
        if question.count() == 0:
            return None
        else:
            return "/api/v1/question/%d/" % question.all()[0].id
        # TODO improve url

    def dehydrate_videoID(self, bundle):
        return extract_YT_video_id(bundle.obj.video)

    def dehydrate_correct(self, bundle):
        questions = bundle.obj.question_set.all()
        if questions.count() == 0:
            # no question: a kq is correct if it is completed
            return self._is_completed(self.user_activity, bundle.obj)
        else:
            question = questions[0]  # there should be only one question
            answer = self.user_answers['questions'].get(unicode(question.id))
            if answer is None:
                return False

            return question.is_correct(answer)

    def dehydrate_completed(self, bundle):
        return self._is_completed(self.user_activity, bundle.obj)

    def _is_completed(self, activity, kq):
        course_id = kq.unit.course.id
        visited = activity['courses'].get(unicode(course_id), None)
        if visited is None:
            return False

        kqs = visited.get('kqs', None)
        if kqs is None:
            return False

        return unicode(kq.id) in kqs


class AttachmentResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = Attachment.objects.all()
        resource_name = 'attachment'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def dehydrate_attachment(self, bundle):
        return bundle.obj.attachment.url


class QuestionResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')
    solutionID = fields.CharField(readonly=True)

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def dehydrate_solutionID(self, bundle):
        return extract_YT_video_id(bundle.obj.solution)

    def dehydrate_last_frame(self, bundle):
        return bundle.obj.last_frame.url


class OptionResource(ModelResource):
    question = fields.ToOneField(QuestionResource, 'question')

    class Meta:
        queryset = Option.objects.all()
        resource_name = 'option'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "question": ('exact'),
        }

    def dispatch(self, request_type, request, **kwargs):
        # We need the request to dehydrate some fields
        collection = get_db().get_collection('answers')
        self.user = get_user(request, collection)
        return super(OptionResource, self).dispatch(request_type, request,
                                                    **kwargs)

    def dehydrate_solution(self, bundle):
        # only return the solution if the user has given an answer
        if self.user:
            answer = self.user['questions'].get(
                unicode(bundle.obj.question.id), None)
        else:
            answer = None

        if answer is None:
            return None
        else:
            return bundle.obj.solution


class AnswerResource(MongoResource):

    class Meta:
        resource_name = 'answer'
        collection = 'answers'
        datakey = 'questions'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "question": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)
        question_id = request.GET.get('question', None)

        results = []
        if question_id is None:
            for qid, question in user['questions'].items():
                if qid == question_id:
                    obj = MongoObj(initial=question)
                    obj.uuid = question_id
                    results.append(obj)
        else:
            question = user['questions'].get(question_id, None)
            if question is not None:
                obj = MongoObj(initial=question)
                obj.uuid = question_id
                results.append(obj)

        return results

    def obj_create(self, bundle, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)

        bundle = self.full_hydrate(bundle)

        if (len(bundle.obj.answer['replyList']) > 0):
            user['questions'][bundle.obj.uuid] = bundle.obj.answer

            self._collection.update({'_id': user['_id']}, user, safe=True)

        bundle.uuid = bundle.obj.uuid

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def hydrate(self, bundle):
        if 'question' in bundle.data:
            question = bundle.data['question']
            pattern = (r'^/api/%s/question/(?P<question_id>[\d+])/$' %
                       self._meta.api_name)
            result = re.findall(pattern, question)
            if result and len(result) == 1:
                bundle.obj.uuid = result[0]

        bundle.obj.answer = {}

        if 'date' in bundle.data:
            bundle.obj.answer['date'] = bundle.data['date']

        if 'replyList' in bundle.data:
            bundle.obj.answer['replyList'] = bundle.data['replyList']

        return bundle

    def dehydrate(self, bundle):
        bundle.data['date'] = bundle.obj.date
        bundle.data['replyList'] = bundle.obj.replyList
        return bundle


class ActivityResource(MongoResource):

    class Meta:
        resource_name = 'activity'
        collection = 'activity'
        datakey = 'courses'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'put']
        filtering = {
            "unit": ('exact'),
        }

    def obj_update(self, bundle, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)
        course_id = kwargs['pk']

        bundle = self.full_hydrate(bundle)

        user[self._meta.datakey][course_id] = bundle.obj.kqs

        self._collection.update({'_id': user['_id']}, user, safe=True)

        bundle.uuid = bundle.obj.uuid

        return bundle

    def hydrate(self, bundle):
        bundle.obj.kqs = {}
        if 'kqs' in bundle.data:
            bundle.obj.kqs['kqs'] = bundle.data['kqs']

        return bundle

    def dehydrate(self, bundle):
        bundle.data['kqs'] = bundle.obj.kqs
        return bundle

    def _initial(self, request, **kwargs):
        course_id = kwargs['pk']
        return {course_id: {'kqs': []}}
