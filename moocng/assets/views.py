# Copyright (c) 2013 Grupo Opentia
# Copyright 2013 Rooter Analysis S.L.
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _


from moocng.assets.models import Asset
from moocng.assets.utils import course_get_assets, user_course_get_reservations, course_get_kq_with_bookable_assets
from moocng.courses.models import Course
from moocng.courses.utils import is_course_ready


@login_required
def course_assets(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview',
                                            args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)

    if not is_ready:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    assets = course_get_assets(course)

    reservations = user_course_get_reservations(request.user, course)

    kqs = course_get_kq_with_bookable_assets(course)

    return render_to_response('assets/assets.html', {
        'course': course,
        'assets': assets,
        'is_enrolled': is_enrolled,
        'reservations': reservations,
        'kqs': kqs
    }, context_instance=RequestContext(request))
