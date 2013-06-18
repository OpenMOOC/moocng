# Copyright 2013 Rooter Analysis S.L.
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

from .views import (CourseReview, CourseReviewAssign, CourseReviewReview,
                    GetS3UploadUrl, GetS3DownloadUrl, CourseReviewUpload)

urlpatterns = patterns(
    'moocng.peerreview.views',

    url(r'^course/(?P<course_slug>[-\w]+)/reviews/$', CourseReview.as_view(),
        name='course_reviews'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/(?P<assignment_id>\d+)/assign',
        CourseReviewAssign.as_view(), name='course_review_assign'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/(?P<assignment_id>\d+)/review/',
        CourseReviewReview.as_view(), name='course_review_review'),
    url(r'^s3_upload_url/', GetS3UploadUrl.as_view(), name='get_s3_upload_url'),
    url(r'^s3_download_url/', GetS3DownloadUrl.as_view(), name='get_s3_download_url'),
    url(r'^course/(?P<course_slug>[-\w]+)/reviews/upload/',
        CourseReviewUpload.as_view(), name='course_review_upload'),
)
