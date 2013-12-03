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

js_info_dict = {
    'packages': ('moocng',),
}

urlpatterns = patterns(
    'moocng.portal.views',
    url(r'^i18n/setlang/$', 'set_language', name='set_language'),
    # JavaScript translations
    url(r'^i18n/js/$', 'cached_javascript_catalog', js_info_dict, name='jsi18n'),
    url(r'^announcements/$', 'announcements', name='portal_announcements'),
    url(r'^announcements/(?P<announcement_id>\d+)/(?P<announcement_slug>[-\w]+)/$',
        'announcement_detail', name='portal_announcement_detail'),

)
