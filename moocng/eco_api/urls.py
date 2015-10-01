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



urlpatterns = patterns(
    'moocng.eco_api.views',
    url(r'^oai/$', 'ListRecords', name='ListRecords'),


    url(r'^heartbeat', 'heartbeat', name='heartbeat'),
    url(r'^users/(?P<id>[-\w]+)/courses', 'courses_by_users', name='heartbeat'),
    url(r'^teachers/(?P<id>[-\w]+)/', 'teacher', name='heartbeat')
)
