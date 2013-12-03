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
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views import i18n
from django.views.decorators.cache import cache_page

from moocng.courses.models import Announcement
from moocng.utils import use_cache


def set_language(request):
    response = i18n.set_language(request)
    if request.method == 'POST':
        site = get_current_site(request)
        lang_code = request.POST.get('language', None)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME,
                            lang_code,
                            domain=site.domain,
                            httponly=False)
    return response


# every time the server is restarted key_prefix will be different
# effectively invalidating this cache
@cache_page(3600, key_prefix='jsi18n-%s' % time.time())
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return i18n.javascript_catalog(request, domain, packages)


def announcements(request):
    announcements = Announcement.objects.portal()
    return render_to_response('portal/announcements.html', {
        'announcements': announcements,
        'use_cache': use_cache(request.user)
    }, context_instance=RequestContext(request))


def announcement_detail(request, announcement_id, announcement_slug):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    return render_to_response('courses/announcement.html', {
        'announcement': announcement,
        'template_base': 'base.html'
    }, context_instance=RequestContext(request))
