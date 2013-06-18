# Copyright 2012 Rooter Analysis S.L.
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

from moocng.courses.feeds import AnnouncementFeed
from moocng.courses.views import (HomeView, FlatPageView, TranscriptView,
                                  CourseAddView, CourseOverviewView,
                                  CourseClassroomView, CourseProgressView,
                                  AnnouncementDetailView)


urlpatterns = patterns(
    'moocng.courses.views',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^course/$', RedirectView.as_view(url='/'), name='course-index'),

    # Flatpages
    url(r'^faq/$', FlatPageView.as_view(), {'page': 'faq'}, name='faq'),
    url(r'^methodology/$', FlatPageView.as_view(), {'page': 'methodology'},
        name='methodology'),
    url(r'^legal/$', FlatPageView.as_view(), {'page': 'legal'}, name='legal'),
    url(r'^tos/$', FlatPageView.as_view(), {'page': 'tos'}, name='tos'),
    url(r'^copyright/$', FlatPageView.as_view(), {'page': 'copyright'}, name='copyright'),
    url(r'^cert/$', FlatPageView.as_view(), {'page': 'cert'}, name='cert'),
    url(r'^oldscore-help/$', FlatPageView.as_view(), {'page': 'oldscore'}, name='oldscore'),
    url(r'^score-help/$', FlatPageView.as_view(), {'page': 'score'}, name='score'),

    url(r'^transcript/$', TranscriptView.as_view(), name='transcript'),

    url(r'^course/add$', CourseAddView.as_view(), name='course_add'),
    url(r'^course/(?P<course_slug>[-\w]+)/$', CourseOverviewView.as_view(),
        name='course_overview'),
    url(r'^course/(?P<course_slug>[-\w]+)/classroom/$', CourseClassroomView.as_view(),
        name='course_classroom'),
    url(r'^course/(?P<course_slug>[-\w]+)/progress/$', CourseProgressView.as_view(),
        name='course_progress'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcement/(?P<announcement_id>\d+)/(?P<announcement_slug>[-\w]+)$',
        AnnouncementDetailView.as_view(), name='announcement_detail'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcements_feed/$',
        AnnouncementFeed(), name='announcements_feed'),

    # Teacher's course administration
    url(r'^course/(?P<course_slug>[-\w]+)/teacheradmin/',
        include('moocng.teacheradmin.urls')),
)
