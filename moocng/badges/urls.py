# Copyright 2012 UNED
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
    'moocng.badges.views',
    url(r'^revoked/$', 'revocation_list',
        name='revocation_list'),
    # url(r'^organization/$', 'issuer',
    #   name='issuer'),
    url(r'^assertion/(?P<assertion_uuid>[-\w]+)/$', 'assertion',
        name='assertion'),
    url(r'^badge/(?P<badge_slug>[-\w]+)/$', 'badge',
        name='badge'),

    url(r'^my_badges/$', 'my_badges', name='my_badges'),

    # New badges
    url(r'^assertion/(?P<assertion_uuid>[-\w]+).json$', 'badge_assertion',
        name='badge_assertion'),
    url(r'^badge/(?P<id>[\d]+).json$', 'badge_badge',
        name='badge_badge'),
    url(r'^badge/(?P<id>[\d]+)/image.svg$', 'badge_image',
        name='badge_image'),
    url(r'^assertion/(?P<assertion_uuid>[-\w]+)/image.svg$', 'badge_image',
        name='badge_assertion_image'),
    url(r'^organization/$', 'issuer',
        name='issuer'),
)
