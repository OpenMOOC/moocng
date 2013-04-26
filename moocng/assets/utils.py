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


import datetime

from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.db.models import Q, Count
from django.utils.translation import ugettext as _

from moocng.mongodb import get_db
from moocng.assets import cache
from moocng.assets.models import Asset, AssetAvailability, Reservation
from moocng.courses.models import KnowledgeQuantum, Course
from moocng.courses.utils import send_mail_wrapper


def course_get_assets(course):
    return Asset.objects.filter(available_in__kq__unit__course__id=course.id).distinct()


def course_get_kq_with_bookable_assets(course):
    kq_ids = AssetAvailability.objects.filter(kq__unit__course__id=course.id).values_list('kq', flat=True)
    return KnowledgeQuantum.objects.filter(id__in=kq_ids)


def course_has_assets(course):
    result = cache.get_course_has_assets_from_cache(course)
    if result is None:
        assets = course_get_assets(course)
        result = assets.count() > 0
        cache.set_course_has_assets_in_cache(course, result)
    return result


def user_course_get_reservations(user, course):
    return Reservation.objects.filter(Q(reserved_from__kq__unit__course__id=course.id)
                                      & Q(user__id=user.id))


def user_course_get_active_reservations(user, course, time=None):
    if time is None:
        time = datetime.datetime.now()
    result = user_course_get_reservations(user, course).filter(Q(reservation_begins__lte=time)
                                                               & Q(reservation_ends__gte=time))
    return result


def user_course_get_past_reservations(user, course, time=None):
    if time is None:
        time = datetime.datetime.now()
    result = user_course_get_reservations(user, course).filter(reservation_ends__lt=time).order_by('-reservation_begins')
    return result


def user_course_get_pending_reservations(user, course, time=None):
    if time is None:
        time = datetime.datetime.now()
    result = user_course_get_reservations(user, course).filter(Q(reservation_begins__gt=time)
                                                               & Q(reservation_ends__gt=time)).order_by('reservation_begins')
    return result


def get_concurrent_reservations(reservation):

        reservation_begins = reservation.reservation_begins
        reservation_ends = reservation.reservation_ends
        slot = reservation.slot_id
        asset = reservation.asset
        collisions = Reservation.objects.filter(asset__id=asset.id)
        collisions = collisions.exclude(Q(reservation_begins__gte=reservation_ends)
                                        | Q(reservation_ends__lte=reservation_begins))

        total_reservations = collisions.filter(slot_id=slot).count()

        return total_reservations


def get_suitable_begin_times(slot_duration, date, specific_date=None):
    """This function returns a list containing the times at which a reservation
    might begin, taking as parameters the desired date and the slot duration
    of the asset.
    Date might be either a date or a datetime instance.
    If an specific_date is established, the list will not contain the times previous
    than that date"""
    res = []

    baseDate = datetime.date.fromordinal(date.toordinal())
    entry = datetime.datetime.fromordinal(baseDate.toordinal())

    while entry.date() == baseDate:
        res.append(entry)
        entry += datetime.timedelta(0, slot_duration * 60)
    if specific_date is not None:
        res = filter(lambda x: x > specific_date, res)

    return res


def is_asset_bookable(user, asset, availability, reservation_begins, reservation_ends, old_reservation=None):
    """This method checks if there is possible to create a new reservation
    with the given parameters.
    It returns a tuple whose first parameter is a boolean which specifies if
    it's possible to create the reservation, and if it's not possible the
    second parameter would be a string which specifies why it's not possible
    to create the reservation"""

    is_modification = (old_reservation is not None)

    if not availability.assets.filter(id=asset.id).exists():
        return(False, _('This asset is not available from this nugget.'))

    if reservation_begins > reservation_ends:
        return(False, _('A reservation should not finish before it starts.'))

    reservation_limit = datetime.datetime.today()
    reservation_limit += datetime.timedelta(0, asset.reservation_in_advance * 60)

    if reservation_begins < datetime.datetime.today():
        return (False, _('The specified time is in the past.'))
    if reservation_begins < reservation_limit:
        return (False, _('Not enough time in advance for this reservation'))
    if reservation_begins.date() < availability.available_from or reservation_ends.date() > availability.available_to:
        return (False, _('The specified time is not in the bookable period.'))

    if not is_modification:
        course = availability.kq.unit.course
        if user_course_get_pending_reservations(user, course).count() >= course.max_reservations_pending:
            return (False, _('You have reached the pending reservations limit for this course.'))
        elif user_course_get_reservations(user, course).count() >= course.max_reservations_total:
            return (False, _('You have reached the reservations limit for this course.'))

    collisions = Reservation.objects.filter(asset__id=asset.id)
    collisions = collisions.exclude(Q(reservation_begins__gte=reservation_ends)
                                    | Q(reservation_ends__lte=reservation_begins))
    if is_modification:
        collisions = collisions.exclude(Q(id=old_reservation.id))

    collision_count = collisions.count()
    if collision_count >= (asset.max_bookable_slots * asset.capacity):
        return (False, _("No available places left at selected time."))

    own_collisions = collisions.filter(user__id=user.id)
    if own_collisions.count() >= 1:
        return (False, _('You already have a reservation for the same asset at the same time'))

    return (True, None)


def book_asset(user, asset, availability, reservation_begins, reservation_ends):
    """This method checks if there is possible to create a new reservation
    with the given parameters, and if it's possible it creates the reservation.
    It returns a tuple whose first parameter is a boolean which specifies if
    the reservation was created, and the second element is a message specifying
    that the reservation was created or the reason why it couldn't be created.
    """
    can_create = is_asset_bookable(user, asset, availability, reservation_begins, reservation_ends)
    if not can_create[0]:
        return can_create

    collisions = Reservation.objects.filter(asset__id=asset.id)
    collisions = collisions.exclude(Q(reservation_begins__gte=reservation_ends)
                                    | Q(reservation_ends__lte=reservation_begins))
    slot_load = collisions.values('slot_id').order_by().annotate(Count('slot_id'))

    candidate_slots = filter(lambda x: x['slot_id__count'] < asset.capacity, slot_load)
    if len(candidate_slots) > 0:
        candidate_slots.sort(key=lambda x: x['slot_id__count'])
        slot_id = candidate_slots[0]['slot_id']
    else:
        #All used slots are full
        used_slots = map(lambda x: x['slot_id'], slot_load)
        free_slots = filter(lambda x: x not in used_slots, range(asset.max_bookable_slots))

        if len(free_slots) == 0:
            return (False, _("There's not a free slot available."))

        slot_id = free_slots[0]

    new_reservation = Reservation(user=user, asset=asset, slot_id=slot_id,
                                  reserved_from=availability,
                                  reservation_begins=reservation_begins,
                                  reservation_ends=reservation_ends)

    new_reservation.save()

    return (True, _("Reservation created successfully."))


def send_cancellation_email(reservation):
    subject = _('Your reservation has been cancelled')
    template = 'assets/email_reservation_cancelled.txt'
    context = {
        'user': reservation.user.get_full_name(),
        'asset': reservation.asset.name,
        'kq': reservation.reserved_from.kq,
        'site': Site.objects.get_current().name
    }
    to = [reservation.user.email]
    send_mail_wrapper(subject, template, context, to)


def send_modification_email(reservation):
    subject = _('Your reservation has been modified')
    template = 'assets/email_reservation_modified.txt'
    context = {
        'user': reservation.user.get_full_name(),
        'asset': reservation.asset.name,
        'kq': reservation.reserved_from.kq,
        'site': Site.objects.get_current().name,
        'begin': reservation.reservation_begins,
        'end': reservation.reservation_ends
    }
    to = [reservation.user.email]
    send_mail_wrapper(subject, template, context, to)


def get_reservations_not_compatible_with_slot_duration(asset):
    slot_duration = asset.slot_duration
    query_list = []
    parameter_list = ()
    if slot_duration == 1:
        query_list.append("TRUE")  # All reservations are be compatible
    elif 60 % slot_duration == 0:  # In this case, only minutes need to be checked
        valid_time_list = get_suitable_begin_times(asset.slot_duration,
                                                   datetime.datetime.now())
        valid_minutes_set = set(map(lambda x: x.minute, valid_time_list))
        for valid_minute in valid_minutes_set:
            query_list.append("(extract (minute from reservation_begins) = %s)")
            parameter_list += (valid_minute, )
    else:
        valid_time_list = get_suitable_begin_times(asset.slot_duration,
                                                   datetime.datetime.now())
        for valid_time in valid_time_list:
            query_list.append("""((extract(hour from reservation_begins) = %s)
                              AND (extract (minute from reservation_begins) = %s))""")
            parameter_list += (valid_time.hour, valid_time.minute)

    query = """((mod(CAST((extract(epoch FROM (reservation_ends-reservation_begins))) AS NUMERIC),
                    %s) != 0)
               OR NOT (""" + " OR ".join(query_list) + """)
               OR (extract (second from reservation_begins) != 0))"""
    parameter_list = (slot_duration * 60, ) + parameter_list
    reservations = Reservation.objects.extra(where=[query],
                                             params=parameter_list)
    filter_from = datetime.datetime.now() + datetime.timedelta(minutes=asset.cancelation_in_advance)
    reservations = reservations.filter(Q(asset__id=asset.id)
                                       & Q(reservation_begins__gt=filter_from))
    return reservations


def check_reservations_slot_duration(asset):
    for i in get_reservations_not_compatible_with_slot_duration(asset):
        send_cancellation_email(i)
        i.delete()
