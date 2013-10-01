# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('moocng.externalapps.views',

    #url(r'^$', 'externalapps_index', name='externalapps_index'),

    url(r'^add/',
        'externalapps_add_or_edit',
        name='externalapps_add'),

    url(r'^(?P<external_app_id>\d+)/edit/$',
        'externalapps_add_or_edit',
        name='externalapps_edit'),

    url(r'^(?P<external_app_id>\d+)/delete/$',
        'externalapps_delete',
        name='externalapps_delete'),

     url(r'^$',
        'externalapps_list',
        name='externalapps_list'),
)
