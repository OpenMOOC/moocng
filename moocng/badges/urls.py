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

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'moocng.badges.views',
    url(r'^revoked/$', 'revocation_list',
        name='revocation_list'),
    url(r'^organization/$', 'issuer',
        name='issuer'),
    url(r'^assertion/(?P<assertion_uuid>[-\w]+)/$', 'assertion',
        name='assertion'),
    url(r'^badge/(?P<badge_slug>[-\w]+)/$', 'badge',
        name='badge'),

    url(r'^my_badges/$', 'my_badges', name='my_badges'),

    url(r'^user_badges/(?P<user_pk>[\d]+)/?$', 'user_badges',
        {'mode': 'id'}, name='user_badges', ),
    url(r'^user_badge/(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/?$', 'user_badge',
        {'mode': 'id'}, name='user_badge', ),
    url(r'^badge_image/(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/image/?$', 'badge_image',
        {'mode': 'id'}, name='badge_image'),

    url(r'^user_badges_email/(?P<user_pk>[^/]+)/?$', 'user_badges',
        {'mode': 'email'}, name='user_badges_email'),
    url(r'^user_badge_email/(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/?$', 'user_badge',
        {'mode': 'email'}, name='user_badge_email'),
    url(r'^badge_image_email/(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/image/?$', 'badge_image',
        {'mode': 'email'}, name='badge_image_email'),

)
