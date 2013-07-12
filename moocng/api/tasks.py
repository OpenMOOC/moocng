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


def process_on_submission(submitted, data):
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


@task
def on_answer_created_task(answer_created):
    process_on_submission(answer_created, {'submitted': 1})


@task
def on_answer_updated_task(answer_updated):
    process_on_submission(answer_updated, {})


@task
def on_peerreviewsubmission_created_task(submission_created):
    data = {
        'course_id': submission_created['course'],
        'unit_id': submission_created['unit'],
        'kq_id': submission_created['kq'],
    }
    process_on_submission(data, {'submitted': 1})


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

    process_on_submission(data, increment)
