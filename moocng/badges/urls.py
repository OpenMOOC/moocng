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
    url(r'^(?P<user_pk>[\d]+)/?$', 'user_badges',
        {'mode': 'id'}, name='user_badges', ),
    url(r'^(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/?$', 'user_badge',
        {'mode': 'id'}, name='user_badge', ),
    url(r'^(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/image/?$', 'badge_image',
        {'mode': 'id'}, name='badge_image'),

    url(r'^(?P<user_pk>[^/]+)/?$', 'user_badges',
        {'mode': 'email'}, name='user_badges_email'),
    url(r'^(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/?$', 'user_badge',
        {'mode': 'email'}, name='user_badge_email'),
    url(r'^(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/image/?$', 'badge_image',
        {'mode': 'email'}, name='badge_image_email'),


    url(r'^issuer/', 'openbadge_issuer', name='openbadge_issuer'),
    url(r'^public_key/', 'openbadge_public_key', name='openbadge_public_key'),
    url(r'^assertion/', 'openbadge_assertion', name='openbadge_assertion'),
)
