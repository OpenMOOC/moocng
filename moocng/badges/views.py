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

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from moocng.badges.models import Badge, Award


def badge_image(request, badge_slug, user_id):
    badge = get_object_or_404(Badge, slug=badge_slug)
    try:
        Award.objects.filter(user__id=user_id).get(badge=badge)
        return HttpResponse(badge.image.read(), content_type="image/png")
    except Award.DoesNotExist:
        return HttpResponse(status=404)
