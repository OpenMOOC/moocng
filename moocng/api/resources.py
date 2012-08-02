# -*- coding: utf-8 -*-

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
    unit = fields.ForeignKey(UnitResource, 'unit')
    videoID = fields.CharField(readonly=True)

    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'kq'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "unit": ('exact'),
        }

    def dehydrate_videoID(self, bundle):
        parsed_url = urlparse.urlparse(bundle.obj.video)
        video_id = urlparse.parse_qs(parsed_url.query)
        video_id = video_id['v'][0]
        return video_id


class QuestionResource(ModelResource):
    kq = fields.ForeignKey(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()