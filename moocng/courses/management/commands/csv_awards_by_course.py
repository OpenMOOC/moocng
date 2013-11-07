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

import csv
from HTMLParser import HTMLParser
from optparse import make_option
import StringIO
from zipfile import ZipFile, ZipInfo


from django.core.management.base import BaseCommand, CommandError

from moocng.badges.models import Award
from moocng.courses.models import Course


class Command(BaseCommand):

    help = ("create a zip bundle with csv files with asigned badges per course")

    option_list = BaseCommand.option_list + (
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

        courses = Course.objects.all()

        if not courses:
            raise CommandError("Courses not found")

        if options["filename"].endswith(".zip"):
            self.filename = options["filename"]
        else:
            self.filename = "%s.zip" % options["filename"]

        h = HTMLParser()

        zip = ZipFile(self.filename, mode="w")

        awards_file = StringIO.StringIO()

        awards_csv = csv.writer(awards_file, quoting=csv.QUOTE_ALL)
        headers = ["Course", "Badge", "Number of awards"]
        awards_csv.writerow(headers)

        for course in courses:
            self.message("Calculatiing awards for course %s" % course.slug)

            awards_counter = 0
            badge_name = u''
            if not course.completion_badge is None:
                awards_counter = Award.objects.filter(badge=course.completion_badge).count()
                badge_name = h.unescape(course.completion_badge.title.encode("ascii", "ignore"))
            row = []
            row.append(h.unescape(course.name.encode("ascii", "ignore")))
            row.append(badge_name)
            row.append(awards_counter)
            awards_csv.writerow(row)

        awards_file.seek(0)
        awards_fileinfo = ZipInfo("awards.csv")
        zip.writestr(awards_fileinfo, awards_file.read())
        awards_file.close()
        zip.close()

        self.message("Created %s file" % self.filename)
