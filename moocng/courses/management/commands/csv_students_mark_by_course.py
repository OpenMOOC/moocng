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

import csv
from HTMLParser import HTMLParser
from optparse import make_option
import StringIO
from zipfile import ZipFile, ZipInfo


from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Course
from moocng.courses.marks import calculate_course_mark


class Command(BaseCommand):

    help = ("create a zip bundle with csv files with students (firt_name, "
            "last_name, email)")

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='append',
                    dest='courses',
                    default=[],
                    help='Only list this courses (can repeat this param)'),
        make_option('-f', '--filename',
                    action='store',
                    dest='filename',
                    default="",
                    help="Filename.zip to save the csv files"),
        make_option('-l', '--limit',
                    action='store',
                    dest='limit',
                    default="10000",
                    help="Limit of the users that will be processed"),
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        if not options["filename"]:
            raise CommandError("-f filename.zip is required")

        limit = options["limit"]

        if options["courses"]:
            courses = options["courses"]
            courses = Course.objects.filter(slug__in=options["courses"])
        else:
            courses = Course.objects.all()

        if not courses:
            raise CommandError("Courses not found")

        if options["filename"].endswith(".zip"):
            self.filename = options["filename"]
        else:
            self.filename = "%s.zip" % options["filename"]

        h = HTMLParser()

        zip = ZipFile(self.filename, mode="w")

        for course in courses:
            self.message("Adding course file %s.csv" % course.slug)

            course_file = StringIO.StringIO()

            course_csv = csv.writer(course_file, quoting=csv.QUOTE_ALL)
            headers = ["first_name", "last_name", "email", "mark"]

            course_csv.writerow(headers)

            students = course.students.all()[:limit]
            headers = ["first_name", "last_name", "email"]

            for student in students:
                row = []
                for field in headers:
                    fieldvalue = getattr(student, field)
                    row.append(h.unescape(fieldvalue).encode("ascii", "ignore"))
                mark, mark_info = calculate_course_mark(course, student)
                row.append(mark)
                course_csv.writerow(row)

            course_fileinfo = ZipInfo("%s.csv" % course.slug)

            course_file.seek(0)

            zip.writestr(course_fileinfo, course_file.read())

            course_file.close()

        zip.close()

        self.message("Created %s file" % self.filename)
