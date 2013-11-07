# Copyright 2013 Yaco Sistemas S.L.
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
from django.utils import translation


class LocaleMiddleware(object):
    """This middleware checks if we have a language cookie. In that case we use
    that language"""

    def process_request(self, request):
        try:
            cookie = settings.LANGUAGE_COOKIE_NAME
        except AttributeError:
            cookie = 'language'
        forced_lang = request.GET.get(cookie, None)
        request.forced_lang = forced_lang
        if forced_lang:
            translation.activate(forced_lang)
            request.LANGUAGE_CODE = translation.get_language()
            if hasattr(request, 'session'):
                request.session['django_language'] = forced_lang
