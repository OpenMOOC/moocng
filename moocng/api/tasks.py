# -*- coding: utf-8 -*-

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

from celery import task

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db


@task
def on_activity_created_task(activity_created):
    db = get_db()
    activity = db.get_collection('activity')
    kq = KnowledgeQuantum.objects.get(id=activity_created['kq_id'])
    kq_type = kq.kq_type()

    # KQ
    data = {
        'viewed': 1
    }
    if kq_type == 'Video':
        data['passed'] = 1
    stats_kq = db.get_collection('stats_kq')
    stats_kq_dict = stats_kq.find_and_modify(
        query={'kq_id': activity_created['kq_id']},
        update={'$inc': data},
        safe=True
    )
    if stats_kq_dict is None:
        data['kq_id'] = activity_created['kq_id']
        data['unit_id'] = kq.unit.id
        data['course_id'] = activity_created['course_id']
        if not 'passed' in data:
            data['passed'] = 0
        if kq_type == "PeerReviewAssignment":
            data['submitted'] = 0
            data['reviews'] = 0
            data['reviewers'] = 0
        elif kq_type == "Question":
            data['submitted'] = 0
        stats_kq.insert(data, safe=True)

    # UNIT
    unit_activity = activity.find({
        'user_id': activity_created['user_id'],
        'unit_id': kq.unit.id
    }).count()
    data = {}
    if unit_activity == 0:  # TODO wrooong, the activity has just  been created
        data['started'] = 1
    elif kq.unit.kq_set.count() == unit_activity:
        data['completed'] = 1
    # TODO passed
    if data.keys():
        stats_unit = db.get_collection('stats_unit')
        stats_unit_dict = stats_unit.find_and_modify(
            query={'unit_id': kq.unit.id},
            update={'$inc': data},
            safe=True
        )
        if stats_unit_dict is None:
            data['course_id'] = activity_created['course_id']
            data['unit_id'] = kq.unit.id
            if not 'started' in data:
                data['started'] = 0
            if not 'completed' in data:
                data['completed'] = 0
            if not 'passed' in data:
                data['passed'] = 0
            stats_unit.insert(data, safe=True)

    # COURSE
    course_activity = activity.find({
        'user_id': activity_created['user_id'],
        'course_id': activity_created['course_id']
    }).count()
    course_kqs = KnowledgeQuantum.objects.filter(unit__course__id=activity_created['course_id']).count()
    data = {}
    if course_activity == 0:  # TODO wrong, the activity has just  been created
        data['started'] = 1
    elif course_kqs == course_activity:
        data['completed'] = 1
    # TODO passed
    if data.keys():
        stats_course = db.get_collection('stats_course')
        stats_course_dict = stats_course.find_and_modify(
            query={'course_id': activity_created['course_id']},
            update={'$inc': data},
            safe=True
        )
        if stats_course_dict is None:
            data['course_id'] = activity_created['course_id']
            if not 'started' in data:
                data['started'] = 0
            if not 'completed' in data:
                data['completed'] = 0
            if not 'passed' in data:
                data['passed'] = 0
            stats_course.insert(data, safe=True)


def on_answer_created_task(answer_created):
    db = get_db()

    # KQ
    data = {
        'submitted': 1
    }
    # TODO passed
    stats_kq = db.get_collection('stats_kq')
    stats_kq_dict = stats_kq.find_and_modify(
        query={'kq_id': answer_created['kq_id']},
        update={'$inc': data},
        safe=True
    )
    if stats_kq_dict is None:
        data['kq_id'] = answer_created['kq_id']
        data['unit_id'] = answer_created['unit_id']
        data['course_id'] = answer_created['course_id']
        data['viewed'] = 0
        if not 'passed' in data:
            data['passed'] = 0
        stats_kq.insert(data, safe=True)

    # UNIT
    data = {}
    # TODO passed
    if data.keys():
        stats_unit = db.get_collection('stats_unit')
        stats_unit_dict = stats_unit.find_and_modify(
            query={'unit_id': answer_created['unit_id']},
            update={'$inc': data},
            safe=True
        )
        if stats_unit_dict is None:
            data['unit_id'] = answer_created['unit_id']
            data['course_id'] = answer_created['course_id']
            data['started'] = 0
            data['completed'] = 0
            stats_unit.insert(data, safe=True)

    # COURSE
    data = {}
    # TODO passed
    if data.keys():
        stats_course = db.get_collection('stats_course')
        stats_course_dict = stats_course.find_and_modify(
            query={'course_id': answer_created['course_id']},
            update={'$inc': data},
            safe=True
        )
        if stats_course_dict is None:
            data['course_id'] = answer_created['course_id']
            data['started'] = 0
            data['completed'] = 0
            stats_course.insert(data, safe=True)
