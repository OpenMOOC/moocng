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

from .views import SetLanguage, CachedJavascriptCatalog

js_info_dict = {
    'packages': ('moocng',),
}

urlpatterns = patterns(
    'moocng.portal.views',
    url(r'^setlang/$', SetLanguage.as_view(), name='set_language'),

    # JavaScript translations
    url(r'^js/$', CachedJavascriptCatalog.as_view(), js_info_dict, name='jsi18n'),
)
