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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from moocng.badges.models import Badge, Award


def user_badges(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        award_list = Award.objects.filter(user__id=user_id)
        return render_to_response('badges/user_badges.html', {
        'award_list': award_list,
        'user': user,
        }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)

def user_badge(request, badge_slug, user_id):
    badge = get_object_or_404(Badge, slug=badge_slug)
    user = get_object_or_404(User, id=user_id)
    try:
        award = get_object_or_404(Award, badge=badge, user=user)
        return render_to_response('badges/user_badge.html', {
        'award': award,
        'user': user,
    }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)

def badge_image(request, badge_slug, user_id):
    badge = get_object_or_404(Badge, slug=badge_slug)
    try:
        Award.objects.filter(user__id=user_id).get(badge=badge)
        return HttpResponse(badge.image.read(), content_type="image/png")
    except Award.DoesNotExist:
        return HttpResponse(status=404)

def user_badges_email(request, user_email):
    user = get_object_or_404(User, email=user_email)
    return user_badges(request, user.id)

def user_badge_email(request, badge_slug, user_email):
    user = get_object_or_404(User, email=user_email)
    return user_badge(request, badge_slug, user.id)

def badge_image_email(request, badge_slug, user_email):
    user = get_object_or_404(User, email=user_email)
    return badge_image(request, badge_slug, user.id)

