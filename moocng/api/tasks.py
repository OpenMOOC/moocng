# -*- coding: utf-8 -*-

# Copyright 2013 UNED
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

import decimal

from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from celery import task

from moocng.badges.models import BadgeByCourse
from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db

from moocng.courses.models import Unit, Course
from moocng.x_api import utils as x_api
from moocng.courses.marks import get_course_mark, get_kq_mark

from datetime import date


@task
def on_activity_created_task(activity_created, unit_activity, course_activity):
    logger = on_activity_created_task.get_logger()
    db = get_db()
    kq = KnowledgeQuantum.objects.get(id=activity_created['kq_id'])
    kq_type = kq.kq_type()
    up_kq, up_u, up_c, passed_kq, passed_unit, passed_course = update_mark(activity_created)
    # KQ
    data = {
        'viewed': 1
    }
    if kq_type == 'Video' or passed_kq:
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

    if passed_unit:
        data['passed'] = 1

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

    if passed_course:
        data['passed'] = 1

    if data.keys():
        stats_course = db.get_collection('stats_course')
        stats_course.update(
            {'course_id': activity_created['course_id']},
            {'$inc': data},
            safe=True
        )


def update_stats(submitted, data_kq=None, data_unit=None, data_course=None):
    db = get_db()
    data_kq = data_kq or {}
    data_unit = data_unit or {}
    data_course = data_course or {}
    # KQ
    if data_kq.keys():
        stats_kq = db.get_collection('stats_kq')
        stats_kq.update(
            {'kq_id': submitted['kq_id']},
            {'$inc': data_kq},
            safe=True
        )

    # UNIT
    if data_unit.keys():
        stats_unit = db.get_collection('stats_unit')
        stats_unit.update(
            {'unit_id': submitted['unit_id']},
            {'$inc': data_unit},
            safe=True
        )

    # COURSE
    if data_course.keys():
        stats_course = db.get_collection('stats_course')
        stats_course.update(
            {'course_id': submitted['course_id']},
            {'$inc': data_course},
            safe=True
        )


def to_decimal(float_price):
    return decimal.Decimal('%.2f' % float_price)


def has_passed_now(new_mark, mark_item, threshold):
    current_mark = mark_item and mark_item['mark'] or None
    if current_mark is None:
        current_mark = 0

    if threshold is None:
        return False
    elif to_decimal(current_mark) >= threshold:
        return False
    elif new_mark is None:
        return False
    return to_decimal(new_mark) >= threshold


def update_kq_mark(db, kq, user, threshold, new_mark_kq=None, new_mark_normalized_kq=None):
    from moocng.courses.marks import calculate_kq_mark

    if not new_mark_kq or not new_mark_normalized_kq:
        new_mark_kq, new_mark_normalized_kq = calculate_kq_mark(kq, user)
    data_kq = {}
    data_kq['user_id'] = user.pk
    data_kq['course_id'] = kq.unit.course.pk
    data_kq['unit_id'] = kq.unit.pk
    data_kq['kq_id'] = kq.pk
    marks_kq = db.get_collection('marks_kq')
    mark_kq_item = marks_kq.find_one(data_kq)
    if mark_kq_item:
        updated_kq_mark = (new_mark_kq != mark_kq_item['mark'] or
                           new_mark_normalized_kq != mark_kq_item['relative_mark'])
        if updated_kq_mark:
            marks_kq.update(
                data_kq,
                {'$set': {'mark': new_mark_kq,
                          'relative_mark': new_mark_normalized_kq}},
                safe=True
            )
    else:
        updated_kq_mark = True
        data_kq['mark'] = new_mark_kq
        data_kq['relative_mark'] = new_mark_normalized_kq
        marks_kq.insert(data_kq)
    if kq.kq_type() == 'PeerReviewAssignment' and threshold is not None:
        threshold = decimal.Decimal('5.0')  # P2P is a special case


    today = date.today()

    # badges
    badges = BadgeByCourse.objects.filter(course_id=kq.unit.course.pk, criteria_type=1)
    for badge in badges:
        win = False
        gotBadge = get_db().get_collection('badge').find_one({'id_badge': badge.id, "id_user": user.pk})
        if(not gotBadge):
            win = True
            criterias = badge.criteria.split(",")
            for criteria in criterias:
                mark = get_db().get_collection('marks_kq').find_one({'user_id': user.pk, "kq_id": int(criteria)})
                if(not mark or mark["mark"] < badge.note):
                    win = False

        if(win):
            get_db().get_collection('badge').insert({"id_badge":badge.id, "id_user":user.pk, "title":badge.title, "description":badge.description, "color":badge.color, "date": today.isoformat() })

    # badge unit checkpoint
    badges = BadgeByCourse.objects.filter(course_id=kq.unit.course_id, criteria_type=0)
    course_mark, units_info = get_course_mark(kq.unit.course, user)
    for badge in badges:
        win = False
        if(badge.note <= course_mark):
            gotBadge = get_db().get_collection('badge').find_one({'id_badge': badge.id, "id_user": user.pk})
            if(not gotBadge):
                try:
                    evaluateUnit = Unit.objects.get(id=badge.criteria)
                    units = Unit.objects.filter(course_id=evaluateUnit.course_id, order__lte = evaluateUnit.order)
                    win = True
                    for aux in units:
                        unit_kqs = aux.knowledgequantum_set.all()
                        for kq in unit_kqs:
                            if not kq.is_completed(user):
                                win = False
                except:
                    pass

        if(win):
            get_db().get_collection('badge').insert({"id_badge":badge.id, "id_user":user.pk, "title":badge.title, "description":badge.description, "color":badge.color, "date": today.isoformat()})

    return updated_kq_mark, has_passed_now(new_mark_kq, mark_kq_item, threshold)


def update_unit_mark(db, unit, user, threshold, new_mark_unit=None, new_mark_normalized_unit=None):
    from moocng.courses.marks import calculate_unit_mark
    if not new_mark_unit or not new_mark_normalized_unit:
        new_mark_unit, new_mark_normalized_unit = calculate_unit_mark(unit, user)
    data_unit = {}
    data_unit['user_id'] = user.pk
    data_unit['course_id'] = unit.course_id
    data_unit['unit_id'] = unit.pk

    marks_unit = db.get_collection('marks_unit')
    mark_unit_item = marks_unit.find_one(data_unit)
    if mark_unit_item:
        updated_unit_mark = (new_mark_unit != mark_unit_item['mark'] or
                             new_mark_normalized_unit != mark_unit_item['relative_mark'])
        if updated_unit_mark:
            marks_unit.update(
                data_unit,
                {'$set': {'mark': new_mark_unit,
                          'relative_mark': new_mark_normalized_unit}},
                safe=True
            )
    else:
        updated_unit_mark = True
        data_unit['mark'] = new_mark_unit
        data_unit['relative_mark'] = new_mark_normalized_unit
        marks_unit.insert(data_unit)

    # check if user completed this unit
    unit_kqs = unit.knowledgequantum_set.all()
    completed = True
    for kq in unit_kqs:
        if not kq.is_completed(user):
            completed = False

    today = date.today()

    if completed:
        # badge unique unit
        badges = BadgeByCourse.objects.filter(course_id=unit.course_id, criteria_type=2)
        for badge in badges:
            win = False
            if(badge.note <= new_mark_unit):
                gotBadge = get_db().get_collection('badge').find_one({'id_badge': badge.id, "id_user": user.pk})
                if(not gotBadge):
                    get_db().get_collection('badge').insert({"id_badge":badge.id, "id_user":user.pk, "title":badge.title, "description":badge.description, "color":badge.color, "date": today.isoformat()})

    return updated_unit_mark, has_passed_now(new_mark_unit, mark_unit_item, threshold)


def update_course_mark(db, course, user, new_mark_course=None):
    from moocng.courses.marks import calculate_course_mark
    if not new_mark_course:
        new_mark_course, units_info = calculate_course_mark(course, user)
    data_course = {}
    data_course['user_id'] = user.pk
    data_course['course_id'] = course.pk
    marks_course = db.get_collection('marks_course')
    mark_course_item = marks_course.find_one(data_course)
    if mark_course_item:
        updated_course_mark = new_mark_course != mark_course_item['mark']
        if updated_course_mark:
            marks_course.update(
                data_course,
                {'$set': {'mark': new_mark_course}},
                safe=True
            )
    else:
        updated_course_mark = True
        data_course['mark'] = new_mark_course
        marks_course.insert(data_course)
    return updated_course_mark, has_passed_now(new_mark_course, mark_course_item, course.threshold)


def update_mark(submitted):
    from moocng.courses.marks import calculate_kq_mark, calculate_unit_mark, calculate_course_mark
    updated_kq_mark = updated_unit_mark = updated_course_mark = False
    passed_kq = passed_unit = passed_course = False
    kq = KnowledgeQuantum.objects.get(pk=submitted['kq_id'])
    unit = kq.unit
    course = kq.unit.course
    user = User.objects.get(pk=submitted['user_id'])
    mark_kq, mark_normalized_kq = calculate_kq_mark(kq, user)

    db = get_db()

    # KQ
    updated_kq_mark, passed_kq = update_kq_mark(db, kq, user, course.threshold,
                                                new_mark_kq=mark_kq,
                                                new_mark_normalized_kq=mark_normalized_kq)

    # UNIT
    if not updated_kq_mark:
        return (updated_kq_mark, updated_unit_mark, updated_course_mark,
                passed_kq, passed_unit, passed_course)

    mark_unit, mark_normalized_unit = calculate_unit_mark(kq.unit, user)
    updated_unit_mark, passed_unit = update_unit_mark(db, unit, user, course.threshold,
                                                      new_mark_unit=mark_unit,
                                                      new_mark_normalized_unit=mark_normalized_unit)

    # COURSE
    if not updated_unit_mark:
        return (updated_kq_mark, updated_unit_mark, updated_course_mark,
                passed_kq, passed_unit, passed_course)
    mark_course, units_info = calculate_course_mark(unit.course, user)

    updated_course_mark, passed_course = update_course_mark(db, course, user, mark_course)
    return (updated_kq_mark, updated_unit_mark, updated_course_mark,
            passed_kq, passed_unit, passed_course)


def get_data_dicts(submitted, passed_kq, passed_unit, passed_course):
    data_kq = {}
    data_unit = {}
    data_course = {}
    if submitted:
        data_kq['submitted'] = submitted

    if passed_kq:
        data_kq['passed'] = 1

    if passed_unit:
        data_unit['passed'] = 1

    if passed_course:
        data_course['passed'] = 1

    return (data_kq, data_unit, data_course)


@task
def on_answer_created_task(answer_created, extra):
    up_kq, up_u, up_c, p_kq, p_u, p_c = update_mark(answer_created)
    submitted = 1
    update_stats(answer_created, *get_data_dicts(submitted, p_kq, p_u, p_c))

    #  xAPI
    user = User.objects.get(pk=answer_created['user_id'])
    course = Course.objects.get(pk=answer_created['course_id'])
    kq = KnowledgeQuantum.objects.get(pk=answer_created['kq_id'])
    resource = {
        'name': kq.title,
        'description': 'Task for course %s' % (course.name),
        'type': 'task',
        'url': 'https://%s%s#unit%s/kq%s/q' % (settings.API_URI, reverse('course_classroom', kwargs={'course_slug': course.slug}), answer_created['unit_id'], answer_created['kq_id'])
    }
    result = {
        'score': float(get_kq_mark(kq, user)) / 10
    }
    x_api.learnerSubmitsAResource(user, resource, course, extra['geolocation'], result=result)


@task
def on_answer_updated_task(answer_updated, extra):
    up_kq, up_u, up_c, p_kq, p_u, p_c = update_mark(answer_updated)
    submitted = 0
    update_stats(answer_updated, *get_data_dicts(submitted, p_kq, p_u, p_c))

    # xAPI
    user = User.objects.get(pk=answer_updated['user_id'])
    course = Course.objects.get(pk=answer_updated['course_id'])
    kq = KnowledgeQuantum.objects.get(pk=answer_updated['kq_id'])
    resource = {
        'name': kq.title,
        'description': 'Task for course %s' % (course.name),
        'type': 'task',
        'url': 'https://%s%s#unit%s/kq%s/q' % (settings.API_URI, reverse('course_classroom', kwargs={'course_slug': course.slug}), answer_updated['unit_id'], answer_updated['kq_id'])
    }
    result = {
        'score': float(get_kq_mark(kq, user)) / 10
    }
    x_api.learnerSubmitsAResource(user, resource, course, extra['geolocation'], result=result)

@task
def on_peerreviewsubmission_created_task(submission_created, extra):
    data = {
        'course_id': submission_created['course'],
        'unit_id': submission_created['unit'],
        'kq_id': submission_created['kq'],
    }
    submitted = 1
    passed = False
    update_stats(data, *get_data_dicts(submitted, passed, passed, passed))

    # xAPI
    user = User.objects.get(pk=submission_created['author'])
    course = Course.objects.get(pk=submission_created['course'])
    kq = KnowledgeQuantum.objects.get(pk=submission_created['kq'])
    resource = {
        'name': kq.title,
        'description': 'Peer assesment for course %s' % (course.name),
        'type': 'assessment',
        'url': 'https://%s%s#unit%s/kq%s/q' % (settings.API_URI, reverse('course_classroom', kwargs={'course_slug': course.slug}), submission_created['unit'], submission_created['kq'])
    }

    x_api.learnerSubmitsAResource(user, resource, course, extra['geolocation'])


@task
def on_peerreviewreview_created_task(review_created, user_reviews, extra):
    data = {
        'course_id': review_created['course'],
        'unit_id': review_created['unit'],
        'kq_id': review_created['kq'],
    }
    data_author = {'user_id': review_created['author']}
    data_author.update(data)
    data_reviewer = {'user_id': review_created['reviewer']}
    data_reviewer.update(data)
    inc_reviewers = 0
    if user_reviews == 1:  # First review of this guy
        inc_reviewers = 1
    datas = [data_author, data_reviewer]
    data_kq = {}
    data_unit = {}
    data_course = {}
    for data in datas:
        up_kq, up_u, up_c, p_kq, p_u, p_c = update_mark(data)
        if p_kq:
            data_kq['passed'] = data_kq.get('passed', 0) + 1
        if p_u:
            data_unit['passed'] = data_unit.get('passed', 0) + 1
        if p_c:
            data_course['passed'] = data_course.get('passed', 0) + 1
    increment = {
        'reviews': 1,
        'reviewers': inc_reviewers
    }
    data_kq.update(increment)
    update_stats(data, data_kq, data_unit, data_course)

    # xAPI
    user = User.objects.get(pk=review_created['author'])
    course = Course.objects.get(pk=review_created['course'])
    kq = KnowledgeQuantum.objects.get(pk=review_created['kq'])
    resource = {
        'name': kq.title,
        'description': 'Peer assesment feedback for course %s' % (course.name),
        'type': 'peerfeedback',
        'url': extra['url']
    }

    x_api.learnerSubmitsAResource(user, resource, course, extra['geolocation'], result=extra['result'])

@task
def on_history_created_task(history_created):
    # Send xAPI event
    print history_created['course_id']
    user = User.objects.get(pk=history_created['user_id'])
    try:
        course = Course.objects.get(pk=history_created['course_id'])
    except:
        course = None
    geolocation = {
        'lat': history_created['lat'],
        'lon': history_created['lon']
    }
    page = {}
    page['url'] = history_created['url']
    if course:
        page['name'] = course.name
        page['description'] = course.name
    else:
        page['name'] = ''
        page['description'] = ''
    x_api.learnerAccessAPage(user, page, course, geolocation)
