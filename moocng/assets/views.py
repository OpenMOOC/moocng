# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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
import pytz

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _


from moocng.assets.models import Asset, AssetAvailability, Reservation
from moocng.assets.utils import (book_asset,
                                 get_concurrent_reservations,
                                 user_course_get_active_reservations,
                                 user_course_get_past_reservations,
                                 user_course_get_pending_reservations)
from moocng.courses.models import KnowledgeQuantum
from moocng.courses.security import get_course_if_user_can_view_or_404
from moocng.courses.utils import is_course_ready

from django.db.models import Q

from datetime import datetime, timedelta


@login_required
def course_reservations(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)

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

    active_reservations = []
    for i in user_course_get_active_reservations(request.user, course):
        base = model_to_dict(i)
        base['concurrent'] = get_concurrent_reservations(i)
        base['asset'] = i.asset
        base['reserved_from'] = i.reserved_from
        active_reservations.append(base)

    past_reservations = []
    for i in user_course_get_past_reservations(request.user, course):
        base = model_to_dict(i)
        base['concurrent'] = get_concurrent_reservations(i)
        base['asset'] = i.asset
        base['reserved_from'] = i.reserved_from
        past_reservations.append(base)

    pending_reservations = []
    for i in user_course_get_pending_reservations(request.user, course):
        base = model_to_dict(i)
        base['concurrent'] = get_concurrent_reservations(i)
        base['asset'] = i.asset
        base['reserved_from'] = i.reserved_from
        pending_reservations.append(base)

    return render_to_response('assets/reservations.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
        'pending_reservations': pending_reservations,
    }, context_instance=RequestContext(request))


@login_required
def cancel_reservation(request, course_slug, reservation_id):

    if request.method in ['POST', 'DELETE']:

        course = get_course_if_user_can_view_or_404(course_slug, request)

        is_enrolled = course.students.filter(id=request.user.id).exists()

        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview',
                                        args=[course_slug]))

        reserv_remove = Reservation.objects.get(Q(id=reservation_id) & Q(user__id=request.user.id))
        if reserv_remove is None:
            messages.error(request, _('You are not the owner of this reservation'))
            return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

        cancel_limit = datetime.utcnow().replace(tzinfo=pytz.utc)
        cancel_limit += timedelta(0, reserv_remove.asset.cancelation_in_advance * 60)

        if reserv_remove.reservation_begins < cancel_limit:
            messages.error(request, _('Not enough time in advance to cancel this reservation.'))
            return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

        reserv_remove.delete()

        return HttpResponseRedirect(reverse('course_reservations', args=[course.slug]))

    else:
        return HttpResponseNotAllowed(['POST', 'DELETE'])


@login_required
def reservation_create(request, course_slug, kq_id, asset_id):

    if request.method in ['POST', 'PUT']:
        course = get_course_if_user_can_view_or_404(course_slug, request)
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
    else:
        return HttpResponseNotAllowed(['POST', 'PUT'])
