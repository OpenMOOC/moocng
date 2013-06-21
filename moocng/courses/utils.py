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

import logging

from datetime import date

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template import loader

from moocng.courses.models import Course


logger = logging.getLogger(__name__)


def is_teacher(user, courses):
    is_teacher = False
    if isinstance(courses, Course):
        courses = [courses]
    if user.is_authenticated():
        for course in courses:
            is_teacher = is_teacher or course.teachers.filter(id=user.id).exists()
    return is_teacher


UNIT_BADGE_CLASSES = {
    'n': 'badge-inverse',
    'h': 'badge-warning',
    'e': 'badge-important',
}


def get_unit_badge_class(unit):
    return UNIT_BADGE_CLASSES[unit.unittype]


def is_course_ready(course):
    has_content = course.unit_set.count() > 0
    is_ready = True
    ask_admin = False
    if course.start_date:
        is_ready = date.today() >= course.start_date
        if is_ready and not has_content:
            is_ready = False
            ask_admin = True
    else:
        if not has_content:
            is_ready = False
            ask_admin = True
    return (is_ready, ask_admin)


def send_mail_wrapper(subject, template, context, to):
    try:
        email = EmailMessage(
            subject=subject,
            body=loader.render_to_string(template, context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to
        )
        email.send()
    except IOError as ex:
        logger.error('The notification "%s" to %s could not be sent because of %s' % (subject, str(to), str(ex)))


def send_mass_mail_wrapper(subject, message, recipients, html_content=False):
    mails = []
    content = message
    if html_content:
        content = ""
    for to in recipients:
        email = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [to])
        if html_content:
            email.attach_alternative(message, "text/html")
        mails.append(email)
    try:
        get_connection().send_messages(mails)
    except IOError as ex:
        logger.error('The massive email "%s" to %s could not be sent because of %s' % (subject, recipients, str(ex)))
