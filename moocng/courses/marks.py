# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

from django.db.models import Sum

from moocng.mongodb import get_db


def calculate_question_mark(kq, question, user):

    """
    Calculate if the user answer is the correct one, and punctuate accordingly.
    If the user did the task right the platform gives a 10, if not, a 0.

    .. versionadded:: 0.1
    """
    db = get_db()
    answers = db.get_collection('answers')
    user_answer = answers.find_one({
        'user_id': user.id,
        'question_id': question.id
    })

    if user_answer:
        mark = question.is_correct(user_answer)
        return mark
    return 0.0


def calculate_peer_review_mark(kq, peer_review_assignment, user):

    """
    Calculate if the user has done the peer reviewed task. This is done by
    checking if the minimum reviews of the task have been done.

    .. versionadded:: 0.1
    """
    from moocng.peerreview.utils import kq_get_peer_review_score

    mark = kq_get_peer_review_score(kq, user,
                                    peer_review_assignment)
    if mark is None:
        mark = 0
    return mark


def calculate_kq_video_mark(kq, user):

    """
    Mark the video as viewed and give the user the punctuation.

    .. versionadded:: 0.1
    """
    if kq.kq_visited_by(user):
        return 10.0
    return 0.0


def calculate_kq_mark(kq, user):

    """
    Calculate is a answer was right or wrong, this is the main function that
    calls the others depending on the content (peerreview, normal, etc.)

    .. warning:: Don't use this in loops

    .. versionadded:: 0.1
    """
    from moocng.peerreview.models import PeerReviewAssignment
    mark = relative_mark = 0

    try:
        question = kq.question_set.get()
        # KQ has a question
        mark = calculate_question_mark(kq, question, user)
    except kq.question_set.model.DoesNotExist:
        try:
            # KQ has a peer review
            pra = kq.peerreviewassignment
            mark = calculate_peer_review_mark(kq, pra, user)
        except PeerReviewAssignment.DoesNotExist:
            # KQ hasn't a question or peer review
            mark = calculate_kq_video_mark(kq, user)
    relative_mark = normalize_kq_weight(kq) * mark / 100.0
    return (mark, relative_mark)


def normalize_kq_weight(kq, unit_kq_counter=None, total_weight_unnormalized=None):
    # KnowledgeQuantumResource does not send unit_kq_counter  [tastypie api]
    if unit_kq_counter is None:
        unit = kq.unit
        total_weight_unnormalized, unit_kq_counter, uni_kqs = get_unit_intermediate_calculations(unit)
    if total_weight_unnormalized == 0:
        if unit_kq_counter == 0:
            return 0
        else:
            return 100.0 / unit_kq_counter
    return (kq.weight * 100.0) / total_weight_unnormalized


def calculate_unit_mark(unit, user, normalized_unit_weight=None):
    """
    Calculate if a unit is approved.

    .. warning:: Don't use this in loops

    .. versionadded:: 0.1
    """

    if normalized_unit_weight is None:
        total_weight_unnormalized, unit_course_counter, course_units = get_course_intermediate_calculations(unit.course)
        normalized_unit_weight = normalize_unit_weight(unit, unit_course_counter, total_weight_unnormalized)
    unit_mark = 0
    kqs = get_kq_info_from_course(unit, user)
    for kq in kqs:
        unit_mark += kq['relative_mark']
    # print "Unit_mark: %d - normalized_unit_weight: %d, normalized_unit_mark: %d" % (unit_mark, normalized_unit_weight, (normalized_unit_weight * unit_mark) / 100.0)
    return (unit_mark, (normalized_unit_weight * unit_mark) / 100.0)


def get_kq_info_from_course(unit, user, db=None):
    db = db or get_db()
    data_unit = {'user_id': user.pk,
                 'unit_id': unit.pk}
    marks_kq = db.get_collection('marks_kq')
    return list(marks_kq.find(data_unit))


def normalize_unit_weight(unit, course_unit_counter, total_weight_unnormalized):
    # print "Unit: %s - Course_unit_counter: %d - total_weight_unnormalized: %d" % (unit, course_unit_counter, total_weight_unnormalized)
    if total_weight_unnormalized == 0:
        if course_unit_counter == 0 or not unit.is_scorable():
            return 0
        else:
            return 100.0 / course_unit_counter
    return (unit.weight * 100.0) / total_weight_unnormalized


def get_course_intermediate_calculations(course):
    course_units = course.unit_set.scorables()
    total_weight_unnormalized = course.unit_set.aggregate(Sum('weight'))['weight__sum']
    unit_course_counter = course_units.count()
    return (total_weight_unnormalized, unit_course_counter, course_units)


def get_unit_intermediate_calculations(unit):
    unit_kqs = unit.knowledgequantum_set.all()
    total_weight_unnormalized = unit_kqs.aggregate(Sum('weight'))['weight__sum']
    unit_kqs_counter = unit_kqs.count()
    return (total_weight_unnormalized, unit_kqs_counter, unit_kqs)


def calculate_course_mark(course, user):
    units_info = get_units_info_from_course(course, user)
    total_mark = sum([unit_info['relative_mark'] for unit_info in units_info])
    return total_mark, units_info


def get_units_info_from_course(course, user, db=None):
    db = db or get_db()
    data_course = {'user_id': user.pk,
                   'course_id': course.pk}
    marks_units = db.get_collection('marks_unit')
    return list(marks_units.find(data_course))


def get_course_mark(course, user, db=None):
    data_course = {'user_id': user.pk,
                   'course_id': course.pk}
    db = db or get_db()
    marks_course = db.get_collection('marks_course')
    mark_course_item = marks_course.find_one(data_course)
    if mark_course_item:
        total_mark = mark_course_item['mark']
    else:
        total_mark = 0
    return (total_mark, get_units_info_from_course(course, user, db=db))

def get_unit_mark(unit, user, db=None):
    data_unit = {   'user_id': user.pk,
                    'unit_id': unit.pk }
    db = db or get_db()
    mark_unit_item = db.get_collection('marks_unit').find(data_unit).limit(1)
    if mark_unit_item:
        mark_unit = mark_unit_item['mark']
    else:
        mark_unit = 0
    return mark_unit

def get_unit_relative_mark(unit, user, db=None):
    data_unit = {   'user_id': user.pk,
                    'unit_id': unit.pk }
    db = db or get_db()
    mark_unit_item = db.get_collection('marks_unit').find(data_unit).limit(1)
    if mark_unit_item:
        mark_unit = mark_unit_item['relative_mark']
    else:
        mark_unit = 0
    return mark_unit

def get_kqs_info_from_unit(unit, user, db=None):
    db = db or get_db()
    data_unit = {'user_id': user.pk,
                   'unit_id': unit.pk}
    marks_kqs = db.get_collection('marks_kq')
    return list(marks_kqs.find(data_unit))

def get_kq_mark(kq, user, db=None):
    data_unit = {   'user_id': user.pk,
                    'kq_id': kq.pk }
    db = db or get_db()
    mark_kq_item = db.get_collection('marks_kq').find(data_unit).limit(1)
    if mark_kq_item and mark_kq_item.count() > 0:
        mark_kq = mark_kq_item[0]['mark']
    else:
        mark_kq = 0

    return mark_kq

def get_kq_relative_mark(kq, user, db=None):
    data_unit = {   'user_id': user.pk,
                    'kq_id': kq.pk }
    db = db or get_db()
    mark_kq_item = db.get_collection('marks_kq').find(data_unit).limit(1)
    if mark_kq_item:
        mark_kq = mark_kq_item['relative_mark']
    else:
        mark_kq = 0
    return mark_kq
