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


from moocng.assets.models import Asset, Reservation
from moocng.assets.utils import course_get_assets, user_course_get_reservations
from moocng.assets.utils import course_get_kq_with_bookable_assets, user_course_get_past_reservations
from moocng.assets.utils import user_course_get_pending_reservations, user_course_get_active_reservations
from moocng.courses.models import Course
from moocng.courses.utils import is_course_ready

from django.db.models import Q

import datetime


@login_required
def course_reservations(request, course_slug):
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

    active_reservations = user_course_get_active_reservations(request.user, course)

    past_reservations = user_course_get_past_reservations(request.user, course)

    pending_reservations = user_course_get_pending_reservations(request.user, course)

    return render_to_response('assets/reservations.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
        'pending_reservations': pending_reservations,
    }, context_instance=RequestContext(request))


@login_required
def cancel_reservation(request, course_slug, reservation_id):

    if request.method == 'POST':

        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()

        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview',
                                        args=[course_slug]))

        reserv_remove = Reservation.objects.filter(Q(id=reservation_id) & Q(user__id=request.user.id))
        if reserv_remove is None:
            messages.error(request, _('You are not the owner of this reservation'))
            return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))
        reserv_remove.delete()

    return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))
