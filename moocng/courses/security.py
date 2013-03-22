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

from datetime import date

from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext as _


from moocng.courses.models import Course, Unit, CourseTeacher


def can_user_view_course(course, user):
    """Returns a pair where the first element is a bool indicating if the user
    can view the course and the second one is a string code explaining the
    reason."""
    if course.is_public:
        return True, 'public'

    if user.is_superuser:
        return True, 'is_superuser'

    if user.is_staff:
        return True, 'is_staff'

    # check if the user is a teacher of the course
    if not user.is_anonymous():
        try:
            CourseTeacher.objects.get(teacher=user, course=course)
            return True, 'is_teacher'
        except CourseTeacher.DoesNotExist:
            pass

    # at this point you don't have permissions to see a course
    return False, 'not_public'


def check_user_can_view_course(course, request):
    """Raises a 404 error if the user can't see the course"""
    yes_he_can, reason = can_user_view_course(course, request.user)

    if yes_he_can:
        if reason != 'public':
            msg_table = {
                'is_staff': _(u'This course is not public yet. Your have access to it because you are staff member'),
                'is_superuser': _(u'This course is not public yet. Your have access to it because you are a super user'),
                'is_teacher': _(u'This course is not public yet. Your have access to it because you are a teacher of the course'),
            }
            messages.warning(request, msg_table[reason])
    else:
        raise Http404()


def get_courses_available_for_user(user):
    """Filter in a list of courses what courses are availabled for the user"""
    if user.is_superuser or user.is_staff:
        # Publish all the courses that are on time.
        return Course.objects.exclude(end_date__lt=date.today())
    elif user.is_anonymous():
        # Only return the published courses
        return Course.objects.exclude(end_date__lt=date.today()).filter(status='p')
    else:
        return Course.objects.exclude(end_date__lt=date.today()).filter(Q(status='p') | Q(status='d', courseteacher__teacher=user))


def can_user_view_unit(unit, user):
    """Returns a pair where the first element is a bool indicating if the user
    can view the unit, and the second one is a string code explaining the
    reason."""

    if unit.status == 'p':
        return True, 'published'

    if user.is_superuser:
        return True, 'is_superuser'

    if user.is_staff:
        return True, 'is_staff'

    # check if the user is a teacher of the course
    if not user.is_anonymous():
        try:
            CourseTeacher.objects.get(teacher=user, course=unit.course)
            return True, 'is_teacher'
        except CourseTeacher.DoesNotExist:
            pass

    if unit.status == 'l':
        return False, 'listable'

    return False, 'draft'


def get_units_available_for_user(course, user):
    """Filter units of a course what courses are availabled for the user"""
    if user.is_superuser or user.is_staff:
        return course.unit_set.all
    elif user.is_anonymous():
        return course.unit_set.filter(Q(status='p') | Q(status='l'))
    else:
        return Unit.objects.filter(Q(status='p', course=course) |
                           Q(status='l', course=course) | 
                           Q(status='d', course=course, course__courseteacher__teacher=user, course__courseteacher__course=course)).distinct()
