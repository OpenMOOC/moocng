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

import gc

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


def calculate_all_stats(user_objects=User.objects,
                        kq_objects=KnowledgeQuantum.objects, callback=None,
                        course_blacklist=[], student_batch=5000):

    counter = 0
    lower = 0
    upper = student_batch
    total = user_objects.all().count()
    all_students = user_objects.only('id').all()
    all_students = [s.id for s in all_students]

    while counter < total:
        db = get_db()
        stats = {}
        activity = db.get_collection('activity')
        submissions = db.get_collection('peer_review_submissions')
        reviews = db.get_collection('peer_review_reviews')
        answers = db.get_collection('answers')
        students = all_students[lower:upper]

        for student_id in students:
            if course_blacklist:
                student_activity = activity.find({
                    'user_id': student_id,
                    'course_id': {'$nin': course_blacklist},
                })
            else:
                student_activity = activity.find({
                    'user_id': student_id,
                })

            student_course_kqs = {}
            student_started_courses = []
            student_unit_kqs = {}
            student_started_units = []

            for act in student_activity:
                cid = act['course_id']
                uid = act['unit_id']
                nid = act['kq_id']

                try:
                    nugget_type = kq_type(kq_objects.only('id').get(id=nid))
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
                        'author': student_id
                    })
                    if submitted.count() > 0:
                        stats[cid]['u'][uid]['n'][nid]['submitted'] += 1

                    revs = reviews.find({
                        'kq': nid,
                        'reviewer': student_id
                    })
                    if revs.count() > 0:
                        stats[cid]['u'][uid]['n'][nid]['reviewers'] += 1
                        stats[cid]['u'][uid]['n'][nid]['reviews'] += revs.count()

                    # TODO passed
                elif nugget_type == 'Question':
                    submitted = answers.find({
                        'kq_id': nid,
                        'user_id': student_id
                    })
                    if submitted.count() > 0:
                        stats[cid]['u'][uid]['n'][nid]['submitted'] += 1

                    # TODO passed

            counter += 1
            if callback is not None:
                callback(step='calculating', counter=counter, total=total)

        store_stats_in_mongo(stats, kq_objects, callback=callback)
        lower = upper
        upper = upper + student_batch
        gc.collect()


def add_field(dictionary, field, value, increment):
    if increment:
        if not '$inc' in dictionary:
            dictionary['$inc'] = {}
        dictionary['$inc'][field] = value
    else:
        dictionary[field] = value


def store_stats_in_mongo(stats, kq_objects, callback=None):
    db = get_db()
    stats_course = db.get_collection('stats_course')
    stats_unit = db.get_collection('stats_unit')
    stats_kq = db.get_collection('stats_kq')

    # TODO move indexes creation to the end if recreating an index is not dangerous
    if stats_course.count() == 0:
        stats_course.create_index([('course_id', 1)])
    if stats_unit.count() == 0:
        stats_unit.create_index([('unit_id', 1)])
    if stats_kq.count() == 0:
        stats_kq.create_index([('kq_id', 1)])

    counter = 0
    total = kq_objects.all().count()  # TODO not a valid metric
    for cid in stats.keys():
        for uid in stats[cid]['u'].keys():
            for nid in stats[cid]['u'][uid]['n'].keys():
                increment = stats_kq.find_one({'kq_id': nid}) is not None

                if increment:
                    nugget = {}
                else:
                    nugget = {
                        'course_id': cid,
                        'unit_id': uid,
                        'kq_id': nid,
                    }

                add_field(nugget, 'viewed', stats[cid]['u'][uid]['n'][nid]['viewed'], increment)
                add_field(nugget, 'passed', stats[cid]['u'][uid]['n'][nid]['passed'], increment)
                if 'reviews' in stats[cid]['u'][uid]['n'][nid]:
                    add_field(nugget, 'submitted', stats[cid]['u'][uid]['n'][nid]['submitted'], increment)
                    add_field(nugget, 'reviews', stats[cid]['u'][uid]['n'][nid]['reviews'], increment)
                    add_field(nugget, 'reviewers', stats[cid]['u'][uid]['n'][nid]['reviewers'], increment)
                elif 'submitted' in stats[cid]['u'][uid]['n'][nid]:
                    add_field(nugget, 'submitted', stats[cid]['u'][uid]['n'][nid]['submitted'], increment)

                stats_kq.update(
                    spec={'kq_id': nid},
                    document=nugget,
                    upsert=True,
                    safe=True
                )

                counter += 1
                if callback is not None:
                    callback(step='storing', counter=counter, total=total)

            increment = stats_unit.find_one({'unit_id': uid}) is not None

            if increment:
                unit = {}
            else:
                unit = {
                    'course_id': cid,
                    'unit_id': uid,
                }

            add_field(unit, 'started', stats[cid]['u'][uid]['started'], increment)
            add_field(unit, 'completed', stats[cid]['u'][uid]['completed'], increment)
            add_field(unit, 'passed', stats[cid]['u'][uid]['passed'], increment)

            stats_unit.update(
                spec={'unit_id': uid},
                document=unit,
                upsert=True,
                safe=True
            )

        increment = stats_course.find_one({'course_id': cid}) is not None

        if increment:
            course = {}
        else:
            course = {
                'course_id': cid,
            }

        add_field(course, 'started', stats[cid]['started'], increment)
        add_field(course, 'completed', stats[cid]['completed'], increment)
        add_field(course, 'passed', stats[cid]['passed'], increment)

        stats_course.update(
            spec={'course_id': cid},
            document=course,
            upsert=True,
            safe=True
        )
