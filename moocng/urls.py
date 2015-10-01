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

from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'


urlpatterns = patterns('',

    url(r'^', include('moocng.eco_api.urls')),

    url(r'^', include('moocng.courses.urls')),

    url(r'^', include('moocng.peerreview.urls')),

    url(r'^', include('moocng.assets.urls')),

    url(r'^enrollment/', include('moocng.enrollment.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^portal/', include('moocng.portal.urls')),

    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^api/', include('moocng.api.urls')),

    url(r'^badges/', include('moocng.badges.urls')),

    url(r'^contact/', include('moocng.contact.urls')),

    url(r'^category/', include('moocng.categories.urls')),

    url(r'^auth/', include('moocng.auth_handlers.urls')),

    url(r'^', include('moocng.profile.urls')),
)

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)


# Grapelli support, in django 1.5 this monkey patching won't be necessary
# because it supports custom user models.
# This monkey patching adds support to the user model of autocompletion.

from django.contrib.auth.models import User

User.autocomplete_search_fields = staticmethod(lambda: ("id__iexact", "username__icontains",))

urlpatterns += patterns('', url(r'^grappelli/', include('grappelli.urls')))
