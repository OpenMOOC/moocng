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

import time

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.views import i18n
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import View


class SetLanguage(View):
    def get(self, request):
        response = i18n.set_language(request)
        return response

    def post(self, request):
        response = i18n.set_language(request)
        site = get_current_site(request)
        lang_code = request.POST.get('language', None)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME,
                            lang_code,
                            domain=site.domain,
                            httponly=False)
        return response

# every time the server is restarted key_prefix will be different
# effectively invalidating this cache
class CachedJavascriptCatalog(View):
    @method_decorator(cache_page(3600, key_prefix='jsi18n-%s' % time.time()))
    def get(self, request, domain='djangojs', packages=None):
        return i18n.javascript_catalog(request, domain, packages)
