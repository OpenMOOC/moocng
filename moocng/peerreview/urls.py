# Copyright 2013 UNED
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

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'moocng.peerreview.views',

    url(r'^course/(?P<course_slug>[-\w]+)/reviews/$', 'course_reviews',
        name='course_reviews'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/kq(?P<kq_id>[-\w]+)/ignorelang/$', 'course_reviews',
        { 'ignore_langs': True }, name='course_reviews_ignorelang'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/(?P<assignment_id>\d+)/assign', 'course_review_assign',
        name='course_review_assign'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/(?P<assignment_id>\d+)/review/', 'course_review_review',
        name='course_review_review'),
    url(r'^s3_upload_url/', 'get_s3_upload_url', name='get_s3_upload_url'),
    url(r'^s3_download_url/', 'get_s3_download_url', name='get_s3_download_url'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/upload/', 'course_review_upload', name='course_review_upload'),
)
