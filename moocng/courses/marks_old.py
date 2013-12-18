# -*- coding: utf-8 -*-
# Copyright 2012-2013 Pablo Martín
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

from moocng.courses.marks import (get_course_intermediate_calculations, normalize_unit_weight,
                                  calculate_question_mark,
                                  calculate_peer_review_mark, calculate_kq_video_mark)


def normalize_kq_weight_old(kq, unit_kq_counter=None, total_weight_unnormalized=None):
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


def calculate_kq_mark_old(kq, user):

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


def calculate_unit_mark_old(unit, user, normalized_unit_weight=None):
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
        mark, use_in_total = calculate_kq_mark_old(unit_kq, user)
        if use_in_total and mark is not None:
            use_unit_in_total = True
            entries.append((unit_kq, mark))
            kqs_total_weight_unnormalized += unit_kq.weight
    kq_unit_counter = len(entries)
    for entry in entries:
        normalized_kq_weight = normalize_kq_weight_old(entry[0], kq_unit_counter, kqs_total_weight_unnormalized)
        unit_mark += (normalized_kq_weight * entry[1]) / 100.0
    if unit_mark == 0:
        return (0, 0, use_unit_in_total)
    else:
        # returns the absolute mark and the mark in relation with the course
        return (unit_mark, (normalized_unit_weight * unit_mark) / 100.0, use_unit_in_total)


def calculate_course_mark_old(course, user):
    total_mark = 0
    units_info = []
    total_weight_unnormalized, unit_course_counter, course_units = get_course_intermediate_calculations(course)
    for unit in course_units:
        unit_info = {}
        use_unit_in_total = False
        normalized_unit_weight = normalize_unit_weight(unit, unit_course_counter, total_weight_unnormalized)
        mark, relative_mark, use_unit_in_total = calculate_unit_mark_old(unit, user, normalized_unit_weight)
        if use_unit_in_total:
            total_mark += relative_mark
        unit_info = {
            'unit': unit,
            'mark': mark,
            'normalized_weight': normalized_unit_weight,
            'use_unit_in_total': use_unit_in_total,
        }
        units_info.append(unit_info)
    return total_mark, units_info
