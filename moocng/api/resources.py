# -*- coding: utf-8 -*-
import re
import random

from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import ModelResource

from moocng.api.authentication import DjangoAuthentication, Authentication
from moocng.api.mongodb import get_db, get_user, get_or_create_user, MongoObj, MongoResource
from moocng.courses.models import Unit, KnowledgeQuantum, Question, Option
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
        # TODO real implementation, not random!!
        # it has to use data from the mongodb to check if the KQ is correct
        rand = random.Random()
        correct = rand.randint(0, 1)
        return correct == 1

    def dehydrate_completed(self, bundle):
        # TODO real implementation, not random!!
        # it has to use data from the mongodb to check if the user has finished
        # the KQ
        rand = random.Random()
        completed = rand.randint(0, 1)
        return completed == 1


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
        return super(OptionResource, self).dispatch(request_type, request, **kwargs)

    def dehydrate_solution(self, bundle):
        # only return the solution if the user has given an answer
        if self.user:
            answer = self.user['questions'].get(unicode(bundle.obj.question.id), None)
        else:
            answer = None

        if answer is None:
            return None
        else:
            return bundle.obj.solution

class AnswerResource(MongoResource):
    collection = 'answers'

    class Meta:
        resource_name = 'answer'
        object_class = MongoObj
        authentication = Authentication()
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "question": ('exact'),
        }

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = str(bundle_or_obj.obj.question)
        else:
            kwargs['pk'] = str(bundle_or_obj.question)

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def obj_get_list(self, request=None, **kwargs):
        user = self._get_or_create_user(request)
        question_id = request.GET.get('question', None)

        results = []
        if question_id is None:
            for qid, question in user['questions'].items():
                if qid == question_id:
                    obj = MongoObj(initial=question)
                    obj.question = question_id
                    results.append(obj)
        else:
            question = user['questions'].get(question_id, None)
            if question is not None:
                obj = MongoObj(initial=question)
                obj.question = question_id
                results.append(obj)

        return results

    def obj_get(self, request=None, **kwargs):
        user = self._get_or_create_user(request)
        question_id = kwargs['pk']

        answer = user['questions'].get(question_id, None)
        if answer is None:
            raise NotFound('Invalid resource lookup data provided')

        obj = MongoObj(initial=answer)
        obj.question = question_id
        return obj

    def obj_create(self, bundle, request=None, **kwargs):
        user = self._get_or_create_user(request)

        bundle = self.full_hydrate(bundle)

        if (len(bundle.obj.answer['replyList']) > 0):
            user['questions'][bundle.obj.question] = bundle.obj.answer

            self._collection.update({'_id': user['_id']}, user, safe=True)

        bundle.uuid = bundle.obj.question

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def hydrate(self, bundle):
        if 'question' in bundle.data:
            question = bundle.data['question']
            pattern = r'^/api/%s/question/(?P<question_id>[\d+])/$' % self._meta.api_name
            result = re.findall(pattern, question)
            if result and len(result) == 1:
                bundle.obj.question = result[0]

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

    def _get_or_create_user(self, request):
        return get_or_create_user(request, self._collection)
