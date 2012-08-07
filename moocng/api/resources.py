# -*- coding: utf-8 -*-

import random
import urlparse

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from moocng.api.authentication import DjangoAuthentication
from moocng.courses.models import Unit, KnowledgeQuantum, Question


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
        parsed_url = urlparse.urlparse(bundle.obj.video)
        video_id = urlparse.parse_qs(parsed_url.query)
        video_id = video_id['v'][0]
        return video_id

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

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }
