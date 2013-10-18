# -*- coding: utf-8 -*-

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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from moocng.badges.models import Badge, Award, Revocation, build_absolute_url
import json


@login_required
def my_badges(request):
    try:
        award_list = Award.objects.filter(user=request.user)
        return render_to_response('badges/my_badges.html', {
            'award_list': award_list,
            'user': request.user,
            'openbadges_service_url': settings.BADGES_SERVICE_URL,
        }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def badge_image(request, badge_slug, user_pk, mode):
    badge = get_object_or_404(Badge, slug=badge_slug)
    if mode == 'email':
        user = get_object_or_404(User, email=user_pk)
    else:
        user = get_object_or_404(User, id=user_pk)
    try:
        Award.objects.filter(user=user).get(badge=badge)
        return HttpResponse(badge.image.read(), content_type="image/png")
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def badge(request, badge_slug):
    badge = get_object_or_404(Badge, slug=badge_slug)
    return HttpResponse(json.dumps(badge.to_dict()))


def revocation_list(request):
    revocations = [r.to_dict() for r in Revocation.objects.all()]

    return HttpResponse(json.dumps(revocations))


def issuer(request):
    issuer = {
        'name': settings.BADGES_ISSUER_NAME,
        'image': settings.BADGES_ISSUER_IMAGE,
        'url': settings.BADGES_ISSUER_URL,
        'email': settings.BADGES_ISSUER_EMAIL,
        'revocationList': build_absolute_url(reverse('revocation_list'))
    }
    return HttpResponse(json.dumps(issuer))


def assertion(request, assertion_uuid):
    assertion = get_object_or_404(Award, uuid=assertion_uuid)
    if assertion.revoked:
        return HttpResponseGone(json.dumps({'revoked': True}))

    return HttpResponse(json.dumps(assertion.to_dict()))
