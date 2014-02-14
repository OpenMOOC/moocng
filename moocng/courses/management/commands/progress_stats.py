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

import csv
from HTMLParser import HTMLParser
from optparse import make_option
import StringIO
from zipfile import ZipFile, ZipInfo


from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Course, Unit, KnowledgeQuantum, Question
from moocng.mongodb import get_db


class Command(BaseCommand):

    help = ("create a zip bundle with csv files with progress stats "
            "(unit_title, unit_passed, kq_title, kq_viewed, kq_answered, "
            "kq_submited, kq_reviewed, kq_passed)")

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='append',
                    dest='course',
                    default=[],
                    help='Course slug'),
        make_option('-f', '--filename',
                    action='store',
                    dest='filename',
                    default="",
                    help="Filename.zip to save the csv files"),
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        if not options["filename"]:
            raise CommandError("-f filename.zip is required")

        if options["course"]:
            courses = Course.objects.filter(slug__in=options["course"])
            if not courses:
                raise CommandError("Course slug not found")
            else:
                course = courses[0]
        else:
            raise CommandError("Course slug not defined")

        if options["filename"].endswith(".zip"):
            self.filename = options["filename"]
        else:
            self.filename = "%s.zip" % options["filename"]

        h = HTMLParser()

        zip = ZipFile(self.filename, mode="w")

        self.message("Calculating course stats ... file %s.csv" % course.slug)

        course_file = StringIO.StringIO()

        course_csv = csv.writer(course_file, quoting=csv.QUOTE_ALL)

        threshold = float(course.threshold)

        units = Unit.objects.filter(course=course)
        kq_headers = ["unit_title", "unit_passed", "kq_title", "kq_viewed",
                      "kq_answered", "kq_submited", "kq_reviewed", "kq_passed"]
        course_csv.writerow(kq_headers)

        db = get_db()
        answers = db.get_collection('answers')
        activities = db.get_collection('activity')
        peer_review_submissions = db.get_collection('peer_review_submissions')
        peer_review_reviews = db.get_collection('peer_review_reviews')

        for i, unit in enumerate(units):
            self.message('Unit %d (%d of %d) -> "%s"' % (unit.id, i, len(units), unit.title))

            unit_title = h.unescape(unit.title.encode("ascii", "ignore"))
            unit_passed = ''
            if threshold is not None:
                unit_passed = db.database.command(
                    'count', 'marks_unit', query={
                        'unit_id': unit.id,
                        'mark': {'$gt': threshold}
                    })
                unit_passed = int(unit_passed.get('n', -1))

            kqs = KnowledgeQuantum.objects.filter(unit=unit)
            for j, kq in enumerate(kqs):
                self.message('Nugget %d (%d of %d) -> "%s"' % (kq.id, j, len(kqs), kq.title))

                kq_title = h.unescape(kq.title.encode("ascii", "ignore"))
                kq_type = kq.kq_type()
                kq_answered = ''
                kq_submited = ''
                kq_reviewed = ''

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

                row = []
                row.append(unit_title)
                row.append(unit_passed)
                row.append(kq_title)
                row.append(kq_viewed)
                row.append(kq_answered)
                row.append(kq_submited)
                row.append(kq_reviewed)
                row.append(kq_passed)
                course_csv.writerow(row)

        course_fileinfo = ZipInfo("%s.csv" % course.slug)

        course_file.seek(0)

        zip.writestr(course_fileinfo, course_file.read())

        course_file.close()

        zip.close()

        self.message("Created %s file" % self.filename)
