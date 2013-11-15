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

from django.contrib.auth.models import User

from celery import task

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db


@task
def on_activity_created_task(activity_created, unit_activity, course_activity):
    db = get_db()
    kq = KnowledgeQuantum.objects.get(id=activity_created['kq_id'])
    kq_type = kq.kq_type()

    # KQ
    data = {
        'viewed': 1
    }
    if kq_type == 'Video':
        data['passed'] = 1
    stats_kq = db.get_collection('stats_kq')
    stats_kq.update(
        {'kq_id': activity_created['kq_id']},
        {'$inc': data},
        safe=True
    )

    # UNIT
    data = {}
    if unit_activity == 1:  # First activity of the unit
        data['started'] = 1
    elif kq.unit.knowledgequantum_set.count() == unit_activity:
        data['completed'] = 1
    # TODO passed
    if data.keys():
        stats_unit = db.get_collection('stats_unit')
        stats_unit.update(
            {'unit_id': kq.unit.id},
            {'$inc': data},
            safe=True
        )

    # COURSE
    course_kqs = KnowledgeQuantum.objects.filter(unit__course__id=activity_created['course_id']).count()
    data = {}
    if course_activity == 1:  # First activity of the course
        data['started'] = 1
    elif course_kqs == course_activity:
        data['completed'] = 1
    # TODO passed
    if data.keys():
        stats_course = db.get_collection('stats_course')
        stats_course.update(
            {'course_id': activity_created['course_id']},
            {'$inc': data},
            safe=True
        )


def update_stats(submitted, data):
    db = get_db()

    # KQ
    # TODO passed
    stats_kq = db.get_collection('stats_kq')
    stats_kq.update(
        {'kq_id': submitted['kq_id']},
        {'$inc': data},
        safe=True
    )

    # UNIT
    data = {}
    # TODO passed
    if data.keys():
        stats_unit = db.get_collection('stats_unit')
        stats_unit.update(
            {'unit_id': submitted['unit_id']},
            {'$inc': data},
            safe=True
        )

    # COURSE
    data = {}
    # TODO passed
    if data.keys():
        stats_course = db.get_collection('stats_course')
        stats_course.update(
            {'course_id': submitted['course_id']},
            {'$inc': data},
            safe=True
        )


def update_kq_score(db, kq, user, new_score_kq=None):
    from moocng.courses.marks import calculate_kq_mark
    if not new_score_kq:
        new_score_kq, use_in_total = calculate_kq_mark(kq, user)
        if not use_in_total:
            return False
    data_kq = {}
    data_kq['user_id'] = user.pk
    data_kq['course_id'] = kq.unit.course.pk
    data_kq['unit_id'] = kq.unit.pk
    data_kq['kq_id'] = kq.pk

    scores_kq = db.get_collection('scores_kq')
    score_kq_item = scores_kq.find_one(data_kq)
    if score_kq_item:
        updated_kq_score = new_score_kq == score_kq_item['score']
        scores_kq.update(
            data_kq,
            {'$set': {'score': new_score_kq}},
            safe=True
        )
    else:
        updated_kq_score = True
        data_kq['score'] = new_score_kq
        scores_kq.insert(data_kq)
    return updated_kq_score


def update_unit_score(db, unit, user, new_score_unit=None):
    from moocng.courses.marks import calculate_unit_mark
    if not new_score_unit:
        new_score_unit, score_normalized_unit, use_unit_in_total = calculate_unit_mark(unit, user)
        if not use_unit_in_total:
            return False
    data_unit = {}
    data_unit['user_id'] = user.pk
    data_unit['course_id'] = unit.course.pk
    data_unit['unit_id'] = unit.pk

    scores_unit = db.get_collection('scores_unit')
    score_unit_item = scores_unit.find_one(data_unit)
    if score_unit_item:
        updated_unit_score = new_score_unit == score_unit_item['score']
        scores_unit.update(
            data_unit,
            {'$set': {'score': new_score_unit}},
            safe=True
        )
    else:
        updated_unit_score = True
        data_unit['score'] = new_score_unit
        scores_unit.insert(data_unit)
    return updated_unit_score


def update_course_score(db, course, user, new_score_course=None):
    from moocng.courses.marks import calculate_course_mark
    if not new_score_course:
        new_score_course, units_info = calculate_course_mark(course, user)
    data_course = {}
    data_course['user_id'] = user.pk
    data_course['course_id'] = course.pk
    scores_course = db.get_collection('scores_course')
    score_course_item = scores_course.find_one(data_course)
    if score_course_item:
        updated_course_score = new_score_course == score_course_item['score']
        scores_course.update(
            data_course,
            {'$set': {'score': new_score_course}},
            safe=True
        )
    else:
        updated_course_score = True
        data_course['score'] = new_score_course
        scores_course.insert(data_course)
    return updated_course_score


def update_score(submitted, data):
    from courses.marks import calculate_kq_mark, calculate_unit_mark, calculate_course_mark
    updated_kq_score = updated_unit_score = updated_course_score = False
    kq = KnowledgeQuantum.objects.get(pk=submitted['kq_id'])
    user = User.objects.get(pk=submitted['user_id'])
    score_kq, use_kq_in_total = calculate_kq_mark(kq, user)
    score_unit, score_normalized_unit, use_unit_in_total = calculate_unit_mark(kq.unit, user)
    score_course, units_info = calculate_course_mark(kq.unit.course, user)
    if not use_kq_in_total:
        return (updated_kq_score, updated_unit_score, updated_course_score)

    db = get_db()

    # KQ
    updated_kq_score = update_kq_score(db, kq, user, score_kq)

    # UNIT
    if not updated_kq_score or not use_unit_in_total:
        return (updated_kq_score, updated_unit_score, updated_course_score)

    updated_unit_score = update_unit_score(db, kq.unit, user, score_unit)

    # COURSE
    if not updated_unit_score:
        return (updated_kq_score, updated_unit_score, updated_course_score)
    updated_course_score = update_course_score(db, kq.unit.course, user, score_course)
    return (updated_kq_score, updated_unit_score, updated_course_score)


@task
def on_answer_created_task(answer_created):
    update_score(answer_created, {'submitted': 1})
    update_stats(answer_created, {'submitted': 1})


@task
def on_answer_updated_task(answer_updated):
    update_stats(answer_updated, {})


@task
def on_peerreviewsubmission_created_task(submission_created):
    data = {
        'course_id': submission_created['course'],
        'unit_id': submission_created['unit'],
        'kq_id': submission_created['kq'],
    }
    update_stats(data, {'submitted': 1})


@task
def on_peerreviewreview_created_task(review_created, user_reviews):
    data = {
        'course_id': review_created['course'],
        'unit_id': review_created['unit'],
        'kq_id': review_created['kq'],
    }

    inc_reviewers = 0
    if user_reviews == 1:  # First review of this guy
        inc_reviewers = 1
    increment = {
        'reviews': 1,
        'reviewers': inc_reviewers
    }

    update_stats(data, increment)
