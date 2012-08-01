# -*- coding: utf-8 -*-

from tastypie.resources import ModelResource
from moocng.courses.models import KnowledgeQuantum


class KnowledgeQuantumResource(ModelResource):
    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'kq'
        allowed_methods = ['get']
