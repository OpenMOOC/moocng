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

import json
import time

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views import i18n
from django.views.decorators.cache import cache_page

from moocng.courses.models import Announcement


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
    if announcements.exists():
        view_announcement = announcements[0]
    else:
        view_announcement = None
    return render_to_response('portal/announcements.html', {
        'announcements': announcements,
        'view_announcement': view_announcement,
    }, context_instance=RequestContext(request))


def announcement_detail(request, announcement_id, announcement_slug):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    return render_to_response('portal/announcement.html', {
        'announcement': announcement,
        'view_announcement': announcement,
    }, context_instance=RequestContext(request))


def announcements_viewed(request):
    user = request.user
    profile = user.is_authenticated() and user.get_profile() or None
    if not profile:
        return HttpResponseForbidden()
    announcement_id = request.POST.get('announcement_id')
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    if announcement.course:
        return HttpResponseForbidden()
    if not profile.last_announcement or profile.last_announcement.datetime < announcement.datetime:
        profile.last_announcement = announcement
        profile.save()
    return HttpResponse(json.dumps({'ok': True}))
