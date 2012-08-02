# -*- coding: utf-8 -*-

import urlparse

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from moocng.courses.models import Unit, KnowledgeQuantum


class UnitResource(ModelResource):

    class Meta:
        queryset = Unit.objects.all()
        resource_name = 'unit'
        allowed_methods = ['get']
        authorization = DjangoAuthorization()

class KnowledgeQuantumResource(ModelResource):
    unit = fields.ForeignKey(UnitResource, 'unit')
    videoID = fields.CharField(readonly=True)

    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'kq'
        allowed_methods = ['get']
        authorization = DjangoAuthorization()
        filtering = {
            "unit": ('exact'),
        }

    def dehydrate_videoID(self, bundle):
        parsed_url = urlparse.urlparse(bundle.obj.video)
        video_id = urlparse.parse_qs(parsed_url.query)
        video_id = video_id['v'][0]
        return video_id
