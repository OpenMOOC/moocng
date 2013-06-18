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

from django.conf.urls import patterns, url

from .views import CourseReservations, CancelReservation, ReservationCreate

urlpatterns = patterns(
    'moocng.assets.views',

    url(r'^course/(?P<course_slug>[-\w]+)/reservations/$', CourseReservations.as_view(),
        name='course_reservations'),
    url(r'^course/(?P<course_slug>[-\w]+)/reservations/(?P<reservation_id>[-\w]+)/cancel$',
        CancelReservation.as_view(), name='cancel_reservation'),
    url(r'^course/(?P<course_slug>[-\w]+)/reservations/(?P<kq_id>[-\w]+)/(?P<asset_id>[-\w]+)/new$',
        ReservationCreate.as_view(), name='reservation_create'),
)
