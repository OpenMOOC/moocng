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
from django.views.generic import RedirectView

from moocng.courses.feeds import AnnouncementCourseFeed


urlpatterns = patterns(
    'moocng.courses.views',
    url(r'^$', 'home', name='home'),
    url(r'^course/$', RedirectView.as_view(url='/'), name='course-index'),

    # Flatpages
    url(r'^faq/$', 'flatpage', {'page': 'faq'}, name='faq'),
    url(r'^methodology/$', 'flatpage', {'page': 'methodology'},
        name='methodology'),
    url(r'^legal/$', 'flatpage', {'page': 'legal'}, name='legal'),
    url(r'^tos/$', 'flatpage', {'page': 'tos'}, name='tos'),
    url(r'^copyright/$', 'flatpage', {'page': 'copyright'}, name='copyright'),
    url(r'^cert/$', 'flatpage', {'page': 'cert'}, name='cert'),
    url(r'^oldscore-help/$', 'flatpage', {'page': 'oldscore'}, name='oldscore'),
    url(r'^score-help/$', 'flatpage', {'page': 'score'}, name='score'),

    url(r'^transcript/$', 'transcript', name='transcript'),
    url(r'^transcript/(?P<course_slug>[-\w]+)/$', 'transcript', name='transcript'),

    url(r'^course/add$', 'course_add', name='course_add'),
    url(r'^course/(?P<course_slug>[-\w]+)/$', 'course_overview',
        name='course_overview'),
    url(r'^course/(?P<course_slug>[-\w]+)/classroom/', 'course_classroom',
        name='course_classroom'),
    url(r'^course/(?P<course_slug>[-\w]+)/syllabus/$', 'course_syllabus',
        name='course_syllabus'),
	url(r'^course/(?P<course_slug>[-\w]+)/dashboard/$', 'course_dashboard',
        name='course_dashboard'),
    url(r'^course/(?P<course_slug>[-\w]+)/progress/$', 'course_progress',
        name='course_progress'),

    url(r'^course/(?P<course_slug>[-\w]+)/forum/$', 'course_forum',
        name='course_forum'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/search/(?P<query>[-\w.]+)/(?P<page>[-\w]+)$', 'course_forum_load_more',
        {'search': True}, name='course_forum_load_more_search'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/hashtag/(?P<query>[-\w.]+)/(?P<page>[-\w]+)$', 'course_forum_load_more',
        {'search': True, 'hashtag': True}, name='course_forum_load_more_hashtag'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/loadMorePosts/(?P<page>[-\w]+)$', 'course_forum_load_more',
        name='course_forum_load_more'),

    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)$', 'course_forum_post',
        name='course_forum_post'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/reply/(?P<reply_id>[-\w.]+)$', 'course_forum_reply',
        name='course_forum_reply'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/upvote/(?P<reply_id>[-\w.]+)$', 'course_forum_vote',
        { 'vote': 1 }, name='course_forum_upvote'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/downvote/(?P<reply_id>[-\w.]+)$', 'course_forum_vote',
        { 'vote': -1 }, name='course_forum_downvote'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/edit/(?P<reply_id>[-\w]+)$', 'course_forum_post_edit',
        name='course_forum_post_edit'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/delete/$', 'course_forum_post_delete',
        name='course_forum_post_delete'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/flag/$', 'course_forum_post_flag',
        name='course_forum_post_flag'),
    url(r'^course/(?P<course_slug>[-\w]+)/forum/(?P<post_id>[-\w]+)/pin/$', 'course_forum_post_pin',
        name='course_forum_post_pin'),

    url(r'^course/(?P<course_slug>[-\w]+)/calendar/$', 'course_calendar',
        name='course_calendar'),
    url(r'^course/(?P<course_slug>[-\w]+)/wiki/$', 'course_wiki',
        name='course_wiki'),
    url(r'^course/(?P<course_slug>[-\w]+)/group/$', 'course_group',
        name='course_group'),
    url(r'^course/(?P<course_slug>[-\w]+)/teachers/$', 'course_teachers',
        name='course_teachers'),
    url(r'^course/(?P<course_slug>[-\w]+)/extra_info/$', 'course_extra_info',
        name='course_extra_info'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcement/(?P<announcement_id>\d+)/(?P<announcement_slug>[-\w]+)$',
        'announcement_detail', name='announcement_detail'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcements_feed/$',
        AnnouncementCourseFeed(), name='announcements_feed'),
    url(r'^course/(?P<course_slug>[-\w]+)/clone-activity/$', 'clone_activity', name='course_clone_activity'),

    url(r'^course/setmark/(?P<knowledgequantumid>\d+)/$','course_setmark',name='course_setmark'),
    url(r'^course/(?P<course_slug>[-\w]+)/checksurvey/(?P<survey_id>[-\w]+)/(?P<survey_token>[-\w]+)$', 'check_survey', name='check_survey'),

    url(r'^course/(?P<course_slug>[-\w]+)/diploma/$', 'course_diploma_pdf', name='course_diploma_pdf'),

    # Teacher's course administration
    url(r'^course/(?P<course_slug>[-\w]+)/teacheradmin/',
        include('moocng.teacheradmin.urls')),

     url(r'^createCourse/(?P<id>[-\w]+)$', 'create_course_groups',
        name='create_course_groups'),

     url(r'^changeGroup/(?P<id_group>[-\w]+)/(?P<id_new_group>[-\w]+)$', 'change_group',
        name='change_group'),
)
