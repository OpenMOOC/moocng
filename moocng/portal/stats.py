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

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db


# We can't use the method in the model because this code can be called from a
# south migration and there is no orm there.
def kq_type(kq):
    if kq.question_set.count() > 0:
        return "Question"
    else:
        try:
            if kq.peerreviewassignment is not None:
                return "PeerReviewAssignment"
        except (ObjectDoesNotExist, AttributeError):
            pass
    return "Video"


def calculate_all_stats(user_objects=None, kq_objects=None, callback=None):
    db = get_db()
    stats = {}
    activity = db.get_collection('activity')
    submissions = db.get_collection('peer_review_submissions')
    reviews = db.get_collection('peer_review_reviews')
    answers = db.get_collection('answers')

    if user_objects is None:
        user_objects = User.objects
    if kq_objects is None:
        kq_objects = KnowledgeQuantum.objects

    counter = 0
    total = user_objects.all().count()
    for student in user_objects.all():
        student_activity = activity.find({'user_id': student.id})

        student_course_kqs = {}
        student_started_courses = []
        student_unit_kqs = {}
        student_started_units = []

        for act in student_activity:
            cid = act['course_id']
            uid = act['unit_id']
            nid = act['kq_id']

            try:
                nugget_type = kq_type(kq_objects.get(id=nid))
            except ObjectDoesNotExist:
                continue

            if not cid in stats:
                stats[cid] = {
                    'u': {},
                    'total_kqs': kq_objects.filter(unit__course__id=cid).count(),
                    'started': 0,
                    'completed': 0,
                    'passed': 0
                }

            if not uid in stats[cid]['u']:
                stats[cid]['u'][uid] = {
                    'n': {},
                    'total_kqs': kq_objects.filter(unit__id=uid).count(),
                    'started': 0,
                    'completed': 0,
                    'passed': 0
                }

            if not nid in stats[cid]['u'][uid]['n']:
                stats[cid]['u'][uid]['n'][nid] = {
                    'viewed': 0,
                    'passed': 0
                }
                if nugget_type == "PeerReviewAssignment":
                    stats[cid]['u'][uid]['n'][nid]['submitted'] = 0
                    stats[cid]['u'][uid]['n'][nid]['reviews'] = 0
                    stats[cid]['u'][uid]['n'][nid]['reviewers'] = 0
                elif nugget_type == "Question":
                    stats[cid]['u'][uid]['n'][nid]['submitted'] = 0

            # Student course stats
            if not cid in student_started_courses:
                stats[cid]['started'] += 1
                student_started_courses.append(cid)

            if not cid in student_course_kqs:
                student_course_kqs[cid] = 0
            student_course_kqs[cid] += 1
            if student_course_kqs[cid] == stats[cid]['total_kqs']:
                stats[cid]['completed'] += 1

            # TODO passed

            # Student unit stats
            if not uid in student_started_units:
                stats[cid]['u'][uid]['started'] += 1
                student_started_units.append(uid)

            if not uid in student_unit_kqs:
                student_unit_kqs[uid] = 0
            student_unit_kqs[uid] += 1
            if student_unit_kqs[uid] == stats[cid]['u'][uid]['total_kqs']:
                stats[cid]['u'][uid]['completed'] += 1

            # TODO passed

            # Student nugget stats
            stats[cid]['u'][uid]['n'][nid]['viewed'] += 1
            if nugget_type == 'PeerReviewAssignment':
                submitted = submissions.find({
                    'kq': nid,
                    'author': student.id
                })
                if submitted.count() > 0:
                    stats[cid]['u'][uid]['n'][nid]['submitted'] += 1

                revs = reviews.find({
                    'kq': nid,
                    'reviewer': student.id
                })
                if revs.count() > 0:
                    stats[cid]['u'][uid]['n'][nid]['reviewers'] += 1
                    stats[cid]['u'][uid]['n'][nid]['reviews'] += revs.count()

                # TODO passed
            elif nugget_type == 'Question':
                submitted = answers.find({
                    'kq_id': nid,
                    'user_id': student.id
                })
                if submitted.count() > 0:
                    stats[cid]['u'][uid]['n'][nid]['submitted'] += 1

                # TODO passed

        counter += 1
        if callback is not None:
            callback(step='calculating', counter=counter, total=total)

    # Store calculated stats
    stats_course = db.get_collection('stats_course')
    stats_unit = db.get_collection('stats_unit')
    stats_kq = db.get_collection('stats_kq')

    counter = 0
    total = kq_objects.all().count()
    for cid in stats.keys():
        for uid in stats[cid]['u'].keys():
            for nid in stats[cid]['u'][uid]['n'].keys():
                nugget = {
                    'course_id': cid,
                    'unit_id': uid,
                    'kq_id': nid,
                    'viewed': stats[cid]['u'][uid]['n'][nid]['viewed'],
                    'passed': 0
                }
                if 'reviews' in stats[cid]['u'][uid]['n'][nid]:
                    nugget['submitted'] = stats[cid]['u'][uid]['n'][nid]['submitted']
                    nugget['reviews'] = stats[cid]['u'][uid]['n'][nid]['reviews']
                    nugget['reviewers'] = stats[cid]['u'][uid]['n'][nid]['reviewers']
                elif 'submitted' in stats[cid]['u'][uid]['n'][nid]:
                    nugget['submitted'] = stats[cid]['u'][uid]['n'][nid]['submitted']

                stats_kq.update(
                    spec={'kq_id': nid},
                    document=nugget,
                    upsert=True,
                    safe=True
                )

                counter += 1
                if callback is not None:
                    callback(step='storing', counter=counter, total=total)

            unit = {
                'course_id': cid,
                'unit_id': uid,
                'started': stats[cid]['u'][uid]['started'],
                'completed': stats[cid]['u'][uid]['completed'],
                'passed': stats[cid]['u'][uid]['passed']
            }

            stats_unit.update(
                spec={'unit_id': uid},
                document=unit,
                upsert=True,
                safe=True
            )

        course = {
            'course_id': cid,
            'started': stats[cid]['started'],
            'completed': stats[cid]['completed'],
            'passed': stats[cid]['passed']
        }

        stats_course.update(
            spec={'course_id': cid},
            document=course,
            upsert=True,
            safe=True
        )


def calculate_course_stats(course):
    db = get_db()
    activity = db.get_collection('activity')
    stats = {
        'course_id': course.id,
        'started': 0,
        'completed': 0,
        'passed': 0
    }
    kqs_count = KnowledgeQuantum.objects.filter(unit__course=course).count()

    for student in course.students.all():
        student_activity = activity.find({
            'course_id': course.id,
            'user_id': student.id
        })
        if student_activity.count() > 0:
            stats['started'] += 1
        if student_activity.count() == kqs_count:
            stats['completed'] += 1
        # TODO passed

    db.get_collection('stats_course').update(
        spec={'course_id': course.id},
        document=stats,
        upsert=True,
        safe=True
    )


def calculate_unit_stats(unit):
    db = get_db()
    activity = db.get_collection('activity')
    stats = {
        'course_id': unit.course.id,
        'unit_id': unit.id,
        'started': 0,
        'completed': 0,
        'passed': 0
    }
    kqs_count = KnowledgeQuantum.objects.filter(unit=unit).count()

    for student in unit.course.students.all():
        student_activity = activity.find({
            'unit_id': unit.id,
            'user_id': student.id
        })
        if student_activity.count() > 0:
            stats['started'] += 1
        if student_activity.count() == kqs_count:
            stats['completed'] += 1
        # TODO passed

    db.get_collection('stats_unit').update(
        spec={'unit_id': unit.id},
        document=stats,
        upsert=True,
        safe=True
    )


def calculate_kq_stats(kq):
    db = get_db()
    activity = db.get_collection('activity')
    stats = {
        'course_id': kq.unit.course.id,
        'unit_id': kq.unit.id,
        'kq_id': kq.id,
        'viewed': 0,
        'passed': 0
    }
    kq_type = kq.kq_type()

    if kq_type == "PeerReviewAssignment":
        stats['submitted'] = 0
        stats['reviews'] = 0
        stats['reviewers'] = 0
        submissions = db.get_collection('peer_review_submissions')
        reviews = db.get_collection('peer_review_reviews')
    elif kq_type == "Question":
        stats['submitted'] = 0
        answers = db.get_collection('answers')

    for student in kq.unit.course.students.all():
        student_activity = activity.find({
            'kq_id': kq.id,
            'user_id': student.id
        })
        if student_activity.count() > 0:
            stats['viewed'] += 1

        if kq_type == 'PeerReviewAssignment':
            submitted = submissions.find({
                'kq': kq.id,
                'author': student.id
            })
            if submitted.count() > 0:
                stats['submitted'] += 1

            revs = reviews.find({
                'kq': kq.id,
                'reviewer': student.id
            })
            if revs.count() > 0:
                stats['reviewers'] += 1
                stats['reviews'] += revs.count()

            # TODO passed
        elif kq_type == 'Question':
            submitted = answers.find({
                'kq_id': kq.id,
                'user_id': student.id
            })
            if submitted.count() > 0:
                stats['submitted'] += 1

            # TODO passed

    db.get_collection('stats_kq').update(
        spec={'kq_id': kq.id},
        document=stats,
        upsert=True,
        safe=True
    )
