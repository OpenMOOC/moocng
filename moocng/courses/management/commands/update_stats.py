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
from datetime import datetime

from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db.models import Max

from moocng.courses.models import Course, Unit, KnowledgeQuantum, Question
from moocng.mongodb import get_db
from bson.code import Code


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--courses',
                    action='store',
                    dest='course_pk',
                    default="",
                    help='Courses pk separated by commas'),
        make_option('-a', '--courses-actives',
                    action='store_true',
                    dest='courses_actives',
                    default=False,
                    help='Only active courses'),
        make_option('-e', '--email-list',
                    action='store',
                    dest='email_list',
                    default="",
                    help='Email recipient list'),
    )

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):
        if options["course_pk"]:
            courses = Course.objects.filter(pk=options["course_pk"])
            if not courses:
                raise CommandError("Course slug not found")
            else:
                course = courses[0]
                course_id = int(options['course_pk'])
        else:
            raise CommandError("Course slug not defined")

        units = Unit.objects.filter(course=options["course_pk"])
        threshold = float(course.threshold)
        course_num_kqs = 0
        db = get_db()
        stats_course = db.get_collection('stats_course')
        stats_unit = db.get_collection('stats_unit')
        stats_kq = db.get_collection('stats_kq')
        answers = db.get_collection('answers')
        activities = db.get_collection('activity')
        peer_review_submissions = db.get_collection('peer_review_submissions')
        peer_review_reviews = db.get_collection('peer_review_reviews')
        marks_course = db.get_collection('marks_course')

        for i, unit in enumerate(units):
            self.message('Unit %d (%d of %d) -> "%s"' % (unit.id, i, len(units), unit.title))

            unit_viewed = len(activities.find({
                'unit_id': unit.id
            }).distinct('user_id'))

            unit_num_kqs = unit.knowledgequantum_set.count()
            course_num_kqs = course_num_kqs + unit_num_kqs
            map = Code("function(){ emit(this.user_id, 1); }")
            reduce = Code("function(key, values){ return Array.sum(values); }")
            unit_completed_mapreduce = activities.map_reduce(map, reduce, "completed_kqs", query={"unit_id": unit.id})
            unit_completed = unit_completed_mapreduce.find({'value': {'$gte': unit_num_kqs}}).count()

            if threshold is not None:
                unit_passed = db.database.command(
                    'count', 'marks_unit', query={
                        'unit_id': unit.id,
                        'mark': {'$gt': threshold}
                    })
                unit_passed = int(unit_passed.get('n', -1))
            else:
                unit_passed = unit_completed

            if (unit_viewed < unit_completed) or (unit_viewed < unit_passed):
                if unit_completed > unit_passed:
                    unit_viewed = unit_completed
                else:
                    unit_viewed = unit_passed

            unit_data = {
                'started': unit_viewed,
                'completed': unit_completed,
                'passed': unit_passed
            }
            stats_unit.update(
                {'unit_id': unit.id},
                {'$set': unit_data},
                safe=True
            )
            self.message('Unit %s (%d) stats -> "%s"' % (unit.title, unit.id, unit_data))

            kqs = KnowledgeQuantum.objects.filter(unit=unit)

            for j, kq in enumerate(kqs):
                self.message('Nugget %d (%d of %d) -> "%s"' % (kq.id, j, len(kqs), kq.title))

                kq_type = kq.kq_type()
                kq_answered = 0
                kq_submited = 0
                kq_reviewed = 0
                kq_reviewers = 0

                kq_viewed = activities.find({
                    'kq_id': kq.id
                }).count()
                kq_passed = kq_viewed

                if threshold is not None and (kq_type == "Question" or
                                              kq_type == "PeerReviewAssignment"):
                    kq_passed = db.database.command(
                        'count', 'marks_kq', query={
                            'kq_id': kq.id,
                            'mark': {'$gt': threshold}
                        })
                    kq_passed = int(kq_passed.get('n', -1))

                if kq_type == "Question":
                    answered = 0
                    questions = Question.objects.filter(kq=kq)
                    for question in questions:
                        answered += answers.find({
                            "question_id": question.id
                        }).count()
                    kq_answered = answered
                elif kq_type == "PeerReviewAssignment":
                    kq_submited = peer_review_submissions.find({
                        'kq': kq.id
                    }).count()
                    kq_reviewed = peer_review_reviews.find({
                        'kq': kq.id
                    }).count()
                    kq_reviewers = len(peer_review_reviews.find({
                        'kq': kq.id
                    }).distinct('reviewer'))

                if (kq_viewed < kq_passed) or (kq_viewed < kq_reviewers) or (kq_viewed < kq_submited):
                    if kq_passed > kq_reviewers and kq_passed > kq_submited:
                        kq_viewed = kq_passed
                    elif kq_passed > kq_reviewers and kq_passed < kq_submited:
                        kq_viewed = kq_submited
                    else:
                        kq_viewed = kq_reviewers

                if kq_reviewed < kq_submited:
                    kq_reviewed = kq_submited

                kq_data = {
                    'submitted': kq_submited,
                    'reviews': kq_reviewed,
                    'reviewers': kq_reviewers,
                    'passed': kq_passed,
                    'viewed': kq_viewed
                }
                stats_kq.update(
                    {'kq_id': kq.id},
                    {'$set': kq_data},
                    safe=True
                )
                self.message('KQ %s (%d) stats -> "%s"' % (kq.title, kq.id, kq_data))

        # Update course
        distinct_course_students = activities.find({ 'course_id': course_id }).distinct('user_id')
        course_started = len(distinct_course_students)

        map = Code("function(){ emit(this.user_id, 1); }")
        reduce = Code("function(key, values){ return Array.sum(values); }")
        course_completed_mapreduce = activities.map_reduce(map, reduce, "completed_kqs", query={"course_id": course.id})
        course_completed = course_completed_mapreduce.find({'value': {'$gt': course_num_kqs}}).count()

        if threshold is not None:
            course_passed = marks_course.find({'course_id': course.id, 'mark': {'$gte': threshold}}).count()
        else:
            course_passed = course_completed

        if (course_started < course_completed) or (course_started < course_passed):
            if course_completed > course_passed:
                course_started = course_completed
            else:
                course_started = course_passed

        course_data = {
            'started': course_started,
            'completed': course_completed,
            'passed': course_passed
        }
        stats_course.update(
            {'course_id': course.id},
            {'$set': course_data},
            safe=True
        )
        self.message('Course %s (%d) stats -> "%s"' % (course.name, course.id, course_data))



       
