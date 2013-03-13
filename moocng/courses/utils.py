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

from datetime import datetime, date

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template import loader

from moocng.mongodb import get_db
from moocng.courses.models import Course


logger = logging.getLogger(__name__)


def calculate_course_mark(course, user):
    from moocng.courses.models import Unit
    use_old_calculus = False
    if course.slug in settings.COURSES_USING_OLD_TRANSCRIPT:
        use_old_calculus = True
    total_mark = 0
    if use_old_calculus:
        course_unit_list = Unit.objects.filter(course=course)
    else:
        course_unit_list = Unit.objects.filter(course=course).exclude(unittype='n')

    total_weight_unnormalized = 0
    for course_unit in course_unit_list:
        total_weight_unnormalized += course_unit.weight

    units_info = []
    for unit in course_unit_list:
        unit_info = {}
        if unit.unittype == 'n' and not use_old_calculus:
            normalized_unit_weight = 0
            mark, relative_mark = (0, 0)
        else:
            normalized_unit_weight = normalize_unit_weight(unit, len(course_unit_list), total_weight_unnormalized)
            mark, relative_mark = calculate_unit_mark(unit, user, normalized_unit_weight)
        total_mark += relative_mark
        unit_info = {
            'unit': unit,
            'mark': mark,
            'normalized_weight': normalized_unit_weight,
        }
        units_info.append(unit_info)
    return total_mark, units_info


def calculate_unit_mark(unit, user, normalized_unit_weight):
    # TODO Optimize per student
    from moocng.courses.models import KnowledgeQuantum
    unit_kqs = KnowledgeQuantum.objects.filter(unit=unit)
    kqs_total_weight_unnormalized = 0
    unit_mark = 0
    entries = []
    for unit_kq in unit_kqs:
        mark, use_in_total = calculate_kq_mark(unit_kq, user)
        if use_in_total and mark is not None:
            entries.append((unit_kq, mark))
            kqs_total_weight_unnormalized += unit_kq.weight
    course_unit_counter = len(entries)
    for entry in entries:
        normalized_kq_weight = normalize_kq_weight(entry[0], course_unit_counter, kqs_total_weight_unnormalized)
        unit_mark += (normalized_kq_weight * entry[1]) / 100.0
    if unit_mark == 0:
        return [0, 0]
    else:
        # returns the absolute mark and the mark in relation with the course
        return [unit_mark, (normalized_unit_weight * unit_mark) / 100.0]


def calculate_kq_mark(kq, user):
    # TODO Optimize per student
    from moocng.courses.models import Question
    from moocng.peerreview.models import PeerReviewAssignment
    from moocng.peerreview.utils import kq_get_peer_review_score
    try:
        db = get_db()
        question = Question.objects.filter(kq=kq)
        if question:
            answers = db.get_collection('answers')
            user_answer_list = answers.find_one({'user': user.id}, safe=True)
            if user_answer_list is not None:
                answer = user_answer_list.get('questions', {}).get(unicode(question[0].id))
                if answer and question[0].is_correct(answer):
                    return (10.0, True)
                else:
                    if kq.unit.deadline is not None and kq.unit.deadline > datetime.now(kq.unit.deadline.tzinfo):
                        return (0.0, True)
        else:
            peer_review_assignment = PeerReviewAssignment.objects.filter(kq=kq)
            if peer_review_assignment:
                mark, use_in_total = kq_get_peer_review_score(kq, user, peer_review_assignment[0])
                return (mark * 2.0, use_in_total)  # * 2 due peer_review range is 1-5
            else:
                activity = db.get_collection('activity')
                user_activity_list = activity.find_one({'user': user.id}, safe=True)
                if user_activity_list is not None:
                    visited_kqs = user_activity_list.get('courses', {}).get(unicode(kq.unit.course.id), {}).get('kqs', [])
                    if unicode(kq.id) in visited_kqs:
                        return (10.0, True)
                    else:
                        if kq.unit.deadline is not None and kq.unit.deadline > datetime.now(kq.unit.deadline.tzinfo):
                            return (0, True)
    except AttributeError:
        pass
    return (0, True)


def normalize_kq_weight(kq, unit_kq_counter=None, total_weight_unnormalized=None):
    # KnowledgeQuantumResource does not send unit_kq_counter  [tastypie api]
    if unit_kq_counter is None:
        from moocng.courses.models import KnowledgeQuantum
        unit_kq_list = KnowledgeQuantum.objects.filter(unit=kq.unit)
        unit_kq_counter = len(unit_kq_list)
        total_weight_unnormalized = 0
        for unit_kq in unit_kq_list:
            total_weight_unnormalized += unit_kq.weight

    if total_weight_unnormalized == 0:
        if unit_kq_counter == 0:
            return 0
        else:
            return 100.0 / unit_kq_counter
    return (kq.weight * 100.0) / total_weight_unnormalized


def normalize_unit_weight(unit, course_unit_counter, total_weight_unnormalized):
    if total_weight_unnormalized == 0:
        if course_unit_counter == 0:
            return 0
        else:
            return 100.0 / course_unit_counter
    return (unit.weight * 100.0) / total_weight_unnormalized


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
            subject = subject,
            body = loader.render_to_string(template, context),
            from_email = settings.DEFAULT_FROM_EMAIL,
            to = to
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
