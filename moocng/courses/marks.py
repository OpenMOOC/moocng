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
        if user_answer and question.is_correct(user_answer):
            return (10.0, True)
        else:
            return (0.0, True)

    return (0.0, True)


def calculate_peer_review_mark(kq, peer_review_assignment, user):

    """
    Calculate if the user has done the peer reviewed task. This is done by
    checking if the minimum reviews of the task have been done.

    .. versionadded:: 0.1
    """
    from moocng.peerreview.utils import kq_get_peer_review_score

    mark, use_in_total = kq_get_peer_review_score(kq, user,
                                                  peer_review_assignment)
    if mark is not None:
        return (mark * 2.0, use_in_total)  # * 2 due peer_review range is 1-5
    else:
        return (None, False)


def calculate_kq_video_mark(kq, user):

    """
    Mark the video as viewed and give the user the punctuation.

    .. versionadded:: 0.1
    """
    if kq.kq_visited_by(user):
        return (10.0, True)
    else:
        return (0, True)


def calculate_kq_mark(kq, user):

    """
    Calculate is a answer was right or wrong, this is the main function that
    calls the others depending on the content (peerreview, normal, etc.)

    .. warning:: Don't use this in loops

    .. versionadded:: 0.1
    """
    from moocng.peerreview.models import PeerReviewAssignment
    try:
        question = kq.question_set.get()
        # KQ has a question
        return calculate_question_mark(kq, question, user)
    except kq.question_set.model.DoesNotExist:
        pass
    else:
        try:
            # KQ has a peer review
            pra = kq.peerreviewassignment
            return calculate_peer_review_mark(kq, pra, user)
        except PeerReviewAssignment.DoesNotExist:
            pass

    # KQ hasn't a question or peer review
    return calculate_kq_video_mark(kq, user)


def calculate_unit_mark(unit, user, normalized_unit_weight=None):
    """
    Calculate if a unit is approved.

    .. warning:: Don't use this in loops

    .. versionadded:: 0.1
    """
    if normalized_unit_weight is None:
        total_weight_unnormalized, unit_course_counter, course_units = get_course_intermediate_calculations(unit.course)
        normalized_unit_weight = normalize_unit_weight(unit, unit_course_counter, total_weight_unnormalized)
    kqs_total_weight_unnormalized = 0
    unit_mark = 0
    entries = []
    use_unit_in_total = False
    for unit_kq in unit.knowledgequantum_set.all():
        mark, use_in_total = calculate_kq_mark(unit_kq, user)
        if use_in_total and mark is not None:
            use_unit_in_total = True
            entries.append((unit_kq, mark))
            kqs_total_weight_unnormalized += unit_kq.weight
    kq_unit_counter = len(entries)
    for entry in entries:
        normalized_kq_weight = normalize_kq_weight(entry[0], kq_unit_counter, kqs_total_weight_unnormalized)
        unit_mark += (normalized_kq_weight * entry[1]) / 100.0
    if unit_mark == 0:
        return (0, 0, use_unit_in_total)
    else:
        # returns the absolute mark and the mark in relation with the course
        return (unit_mark, (normalized_unit_weight * unit_mark) / 100.0, use_unit_in_total)


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


def get_course_intermediate_calculations(course):
    course_units = course.unit_set.scorables()
    total_weight_unnormalized = course.unit_set.aggregate(Sum('weight'))['weight__sum']
    unit_course_counter = course_units.count()
    return (total_weight_unnormalized, unit_course_counter, course_units)


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
