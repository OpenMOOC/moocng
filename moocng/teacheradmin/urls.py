# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

from django.conf.urls import include, patterns, url


urlpatterns = patterns('moocng.teacheradmin.views',

    url(r'^$', 'teacheradmin_info', name='teacheradmin_index'),

    url(r'^stats/$', 'teacheradmin_stats', name='teacheradmin_stats'),

    url(r'^stats/students/$', 'teacheradmin_stats_students', name='teacheradmin_stats_students'),
    url(r'^stats/teachers/$', 'teacheradmin_stats_teachers', name='teacheradmin_stats_teachers'),

    url(r'^stats/units/$', 'teacheradmin_stats_units',
        name='teacheradmin_stats_units'),

    url(r'^stats/kqs/$', 'teacheradmin_stats_kqs',
        name='teacheradmin_stats_kqs'),

    url(r'^units/$', 'teacheradmin_units', name='teacheradmin_units'),

    url(r'^units/forcevideoprocess/$', 'teacheradmin_units_forcevideoprocess',
        name='teacheradmin_units_forcevideoprocess'),

    url(r'^units/attachment/$', 'teacheradmin_units_attachment',
        name='teacheradmin_units_attachment'),

    url(r'^units/transcription/$', 'teacheradmin_units_transcription',
        name='teacheradmin_units_transcription'),

    url(r'^units/s3upload/$', 'teacheradmin_units_s3upload',
        name='teacheradmin_units_s3upload'),

    url(r'^units/question/(?P<kq_id>\d+)/$', 'teacheradmin_units_question',
        name='teacheradmin_units_question'),

    url(r'^units/question/(?P<kq_id>\d+)/(?P<option_id>\d+)/$',
        'teacheradmin_units_option', name='teacheradmin_units_option'),

    url(r'^teachers/$', 'teacheradmin_teachers', name='teacheradmin_teachers'),

    url(r'^teachers/delete/(?P<email_or_id>[^/]+)/$', 'teacheradmin_teachers_delete',
        name='teacheradmin_teachers_delete'),

    url(r'^teachers/invite/$', 'teacheradmin_teachers_invite',
        name='teacheradmin_teachers_invite'),

    url(r'^teachers/reorder/$', 'teacheradmin_teachers_reorder',
        name='teacheradmin_teachers_reorder'),

    url(r'^teachers/transfer/$', 'teacheradmin_teachers_transfer',
        name='teacheradmin_teachers_transfer'),

    url(r'^info/$', 'teacheradmin_info', name='teacheradmin_info'),

    url(r'^groups/$', 'teacheradmin_groups', name='teacheradmin_groups'),


    url(r'^categories/$', 'teacheradmin_categories',
        name='teacheradmin_categories'),

    url(r'^badges/(?P<badge_id>\d+)$', 'teacheradmin_badges',
        name='teacheradmin_badges'),

    url(r'^badges/$', 'teacheradmin_badges',
        name='teacheradmin_badges'),

    url(r'^announcements/$', 'teacheradmin_announcements',
        name='teacheradmin_announcements'),

    url(r'^announcements/add/',
        'teacheradmin_announcements_add_or_edit',
        name='teacheradmin_announcements_add'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/edit/$',
        'teacheradmin_announcements_add_or_edit',
        name='teacheradmin_announcements_edit'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/$',
        'teacheradmin_announcements_view',
        name='teacheradmin_announcements_view'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/delete/$',
        'teacheradmin_announcements_delete',
        name='teacheradmin_announcements_delete'),

    url(r'^emails/$', 'teacheradmin_emails', name='teacheradmin_emails'),

    url(r'^assets/$', 'teacheradmin_assets',
        name='teacheradmin_assets'),

    url(r'^assets/(?P<asset_id>\d+)/edit/$',
        'teacheradmin_assets_edit',
        name='teacheradmin_assets_edit'),



    url(r'^badges/reloadPills/(?P<id>\d+)/$', 'reload_pills',
        name='reload_pills'),

    url(r'^badges/deleteBadge/(?P<id>\d+)/$', 'delete_badge',
        name='delete_badge'),

    # Course's external apps admin
    url(r'^externalapps/', include('moocng.externalapps.urls')),

    url(r'^lists/$', 'teacheradmin_lists', name='teacheradmin_lists'),
    url(r'^lists/coursestudents/$', 'teacheradmin_lists_coursestudents', name='teacheradmin_lists_coursestudents'),
    url(r'^lists/coursestudents/csv$', 'teacheradmin_lists_coursestudents', {'format':'csv'}, name='teacheradmin_lists_coursestudents_csv'),
    url(r'^lists/coursestudentsmarks/$', 'teacheradmin_lists_coursestudentsmarks', name='teacheradmin_lists_coursestudentsmarks'),
    url(r'^lists/coursestudentsmarks/csv$', 'teacheradmin_lists_coursestudentsmarks', {'format':'csv'}, name='teacheradmin_lists_coursestudentsmarks_csv'),
    url(r'^lists/coursestudentsmarks/(?P<filter>[\w]*)/$', 'teacheradmin_lists_coursestudentsmarks', name='teacheradmin_lists_coursestudentsmarks_filter'),
    url(r'^lists/coursestudentsmarks/(?P<filter>[\w]*)/csv$', 'teacheradmin_lists_coursestudentsmarks', {'format':'csv'}, name='teacheradmin_lists_coursestudentsmarks_filter_csv'),
    url(r'^lists/courseteachers$', 'teacheradmin_lists_courseteachers', name='teacheradmin_lists_courseteachers'),
    url(r'^lists/courseteachers/csv$', 'teacheradmin_lists_courseteachers', {'format':'csv'}, name='teacheradmin_lists_courseteachers_csv'),

    url(r'^lists/coursestudents/(?P<username>[-\+@\w.]*)/$', 'teacheradmin_lists_coursestudents_detail', name='teacheradmin_lists_coursestudents_detail'),
)
