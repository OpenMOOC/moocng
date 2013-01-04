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

# -*- coding: utf-8 -*-

from datetime import datetime, date

from moocng.api.mongodb import get_db
from moocng.courses.models import Course


def calculate_unit_mark(unit, user):
    from moocng.courses.models import KnowledgeQuantum
    unit_kqs = KnowledgeQuantum.objects.filter(unit=unit)
    unit_mark = 0
    for unit_kq in unit_kqs:
        mark = calculate_kq_mark(unit_kq, user)
        if mark > 0:
            unit_mark += mark
    if unit_mark == 0:
        return [0, 0]
    else:
        normalized_unit_weight = normalize_unit_weight(unit)
        # returns the absolute mark and the mark in relation with the course
        return [unit_mark, (normalized_unit_weight * unit_mark) / 100.0]


def calculate_kq_mark(kq, user):
    from moocng.courses.models import Question
    try:
        db = get_db()
        question = Question.objects.filter(kq=kq)
        if question:
            answers = db.get_collection('answers')
            user_answer_list = answers.find_one({'user': user.id}, safe=True)
            if user_answer_list is not None:
                answer = user_answer_list.get('questions', {}).get(unicode(question[0].id))
                if answer and question[0].is_correct(answer):
                    return (normalize_kq_weight(kq) * 10.0) / 100
                else:
                    if kq.unit.deadline is not None and kq.unit.deadline > datetime.now():
                        return 0
        else:
            activity = db.get_collection('activity')
            user_activity_list = activity.find_one({'user': user.id}, safe=True)
            if user_activity_list is not None:
                visited_kqs = user_activity_list.get('courses', {}).get(unicode(kq.unit.course.id), {}).get('kqs', [])
                if unicode(kq.id) in visited_kqs:
                    return (normalize_kq_weight(kq) * 10.0) / 100
                else:
                    if kq.unit.deadline is not None and kq.unit.deadline > datetime.now():
                        return 0
    except AttributeError:
        pass
    return -1


def normalize_kq_weight(kq):
    from moocng.courses.models import KnowledgeQuantum
    unit_kq_list = KnowledgeQuantum.objects.filter(unit=kq.unit)
    total_weight = 0
    for unit_kq in unit_kq_list:
        total_weight += unit_kq.weight
    if total_weight == 0:
        return 100.0 / len(unit_kq_list)
    return (kq.weight * 100.0) / total_weight


def normalize_unit_weight(unit):
    from moocng.courses.models import Unit
    course_unit_list = Unit.objects.filter(course=unit.course)
    total_weight = 0
    for course_unit in course_unit_list:
        total_weight += course_unit.weight
    if total_weight == 0:
        return 100.0 / len(course_unit_list)
    return (unit.weight * 100.0) / total_weight


def show_material_checker(course, user):
    show_material = False
    in_time = course.start_date is None or date.today() > course.start_date
    has_privileges = user.is_staff or course.teachers.filter(id=user.id).exists()
    if in_time or has_privileges:
        show_material = True
    return show_material


def is_teacher(user, courses):
    is_teacher = False
    if isinstance(courses, Course):
        courses = [courses]
    if user.is_authenticated():
        for course in courses:
            is_teacher = is_teacher or course.teachers.filter(id=user.id).exists()
    return is_teacher
