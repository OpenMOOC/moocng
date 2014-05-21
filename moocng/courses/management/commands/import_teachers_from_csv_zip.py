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
from optparse import make_option
from zipfile import ZipFile


from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from moocng.courses.models import Course, CourseTeacher


class Command(BaseCommand):

    help = ("create a zip bundle with csv files with teachers (email, "
            "course)")

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
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        if not options["filename"]:
            raise CommandError("-f filename.zip is required")

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

        zip = ZipFile(self.filename, mode="r")

        imported_relations = 0
        for course in courses:
            self.message("Adding course file %s.csv" % course.slug)

            try:
                course_file = zip.open("%s.csv" % course.slug)
            except:
                self.error("Course %s not found in zip file" % course.slug)
                continue

            course_csv = csv.reader(course_file, quoting=csv.QUOTE_ALL)

            course_csv.next()  # skip headers

            order = 0

            for row in course_csv:
                username = row[1]
                if not course.teachers.filter(username=username).exists():
                    teacher = User.objects.get(username=username)
                    CourseTeacher.objects.create(teacher=teacher,
                                                 course=course,
                                                 order=order)
                    self.message("in %s added teacher %s" % (course.slug,
                                                             teacher.username))
                    imported_relations += 1
                    order += 1

            course_file.close()

        zip.close()

        self.message("Imported %s relations from %s file" %
                     (imported_relations, self.filename))
