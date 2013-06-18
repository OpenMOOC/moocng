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
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.generic import View


from moocng.assets.models import Asset, AssetAvailability, Reservation
from moocng.assets.utils import *
from moocng.courses.models import Course, KnowledgeQuantum
from moocng.courses.utils import is_course_ready

from django.db.models import Q

from datetime import datetime, timedelta
import pytz


class CourseReservations(View):
    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview',
                                                args=[course_slug]))

        return render_to_response(
            self.get_template_name(course),
            self.get_context_data(request.user, course),
            context_instance=RequestContext(request))

    def get_template_name(self, course):
        is_ready, ask_admin = is_course_ready(course)
        if is_ready:
            return 'assets/reservations.html'
        else:
            return 'courses/no_content.html'

    def get_context_data(self, user, course):
        is_ready, ask_admin = is_course_ready(course)
        is_enrolled = course.students.filter(id=user.id).exists()

        context = {
            "course": course,
            "is_enrolled": is_enrolled,
        }

        if is_ready:
            active_reservations = self.get_active_reservations(user, course)
            past_reservations = self.get_past_reservations(user, course)
            pending_reservations = self.get_pending_reservations(user, course)

            context['active_reservations'] = active_reservations
            context['past_reservations'] = past_reservations
            context['pending_reservations'] = pending_reservations
        else:
            context['ask_admin'] = ask_admin

        return context

    def get_active_reservations(self, user, course):
        active_reservations = []
        for i in user_course_get_active_reservations(user, course):
            base = model_to_dict(i)
            base['concurrent'] = get_concurrent_reservations(i)
            base['asset'] = i.asset
            base['reserved_from'] = i.reserved_from
            active_reservations.append(base)
        return active_reservations

    def get_past_reservations(self, user, course):
        past_reservations = []
        for i in user_course_get_past_reservations(user, course):
            base = model_to_dict(i)
            base['concurrent'] = get_concurrent_reservations(i)
            base['asset'] = i.asset
            base['reserved_from'] = i.reserved_from
            past_reservations.append(base)
        return past_reservations

    def get_pending_reservations(self, user, course):
        pending_reservations = []
        for i in user_course_get_pending_reservations(user, course):
            base = model_to_dict(i)
            base['concurrent'] = get_concurrent_reservations(i)
            base['asset'] = i.asset
            base['reserved_from'] = i.reserved_from
            pending_reservations.append(base)
        return pending_reservations

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseReservations, self).dispatch(*args, **kwargs)


class CancelReservation(View):
    def post(self, request, course_slug, reservation_id):
        return self.post_and_delete(request, course_slug, reservation_id)

    def delete(self, request, course_slug, reservation_id):
        return self.post_and_delete(request, course_slug, reservation_id)

    def post_and_delete(self, request, course_slug, reservation_id):
        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()

        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview',
                                        args=[course_slug]))

        reserv_remove = Reservation.objects.get(Q(id=reservation_id) & Q(user__id=request.user.id))
        if reserv_remove is None:
            messages.error(request, _('You are not the owner of this reservation'))
            return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

        cancel_limit = datetime.utcnow().replace(tzinfo = pytz.utc)
        cancel_limit += timedelta(0, reserv_remove.asset.cancelation_in_advance * 60)

        if reserv_remove.reservation_begins < cancel_limit:
            messages.error(request, _('Not enough time in advance to cancel this reservation.'))
            return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

        reserv_remove.delete()

        return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CancelReservation, self).dispatch(*args, **kwargs)


class ReservationCreate(View):
    def post(self, request, course_slug, kq_id, asset_id):
        return self.post_and_put(request, course_slug, kq_id, asset_id)

    def put(self, request, course_slug, kq_id, asset_id):
        return self.post_and_put(request, course_slug, kq_id, asset_id)

    def post_and_put(self, request, course_slug, kq_id, asset_id):
        course = get_object_or_404(Course, slug=course_slug)
        is_enrolled = course.students.filter(id=request.user.id).exists()

        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview',
                                                args=[course_slug]))

        kq = get_object_or_404(KnowledgeQuantum, id=kq_id)
        asset = get_object_or_404(Asset, id=asset_id)

        try:
            availability = kq.asset_availability
        except AssetAvailability.DoesNotExist:
            messages.error(request, _('This nugget has no available asset'))
            return HttpResponseRedirect(reverse('course_reservations',
                                        args=[course_slug]))

        if not ('reservation_date' in request.POST and 'reservation_time' in request.POST):
            messages.error(request, _('No initial time specified'))
            return HttpResponseRedirect(reverse('course_reservations',
                                        args=[course_slug]))

        try:
            reservation_starts = datetime.strptime(request.POST['reservation_date'] + ' ' + request.POST['reservation_time'],
                                 '%Y-%m-%d %H:%M')
        except ValueError:
            messages.error(request, _('Incorrect booking time specified'))
            return HttpResponseRedirect(reverse('course_overview',
                                        args=[course_slug]))

        did_book = book_asset(request.user, asset, availability, reservation_starts,
                              reservation_starts + timedelta(0, asset.slot_duration * 60))
        if did_book[0]:
            messages.success(request, did_book[1])
        else:
            messages.error(request, did_book[1])

        return HttpResponseRedirect(reverse('course_reservations',
                                    args=[course_slug]))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReservationCreate, self).dispatch(*args, **kwargs)
