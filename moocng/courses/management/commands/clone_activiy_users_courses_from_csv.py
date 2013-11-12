# -*- coding: utf-8 -*-
# Copyright 2013 Pablo Martín
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
import os

from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Course
from moocng.courses.utils import clone_activiy_user_course


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--csv',
                    action='store',
                    dest='csv_file',
                    default="",
                    help='CSV file'),
    )

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):
        if not options["csv_file"]:
            raise CommandError("--csv / -c param is required")
        csv_path = options["csv_file"]
        if not csv_path.startswith(os.sep):
            csv_path = os.path.join(settings.BASEDIR, csv_path)
        with open(csv_path, 'rb') as csvfile_rb:
            spamreader = csv.reader(csvfile_rb, delimiter=',', quotechar='|')
            for email, old_slug, new_slug in spamreader:
                try:
                    original_course = Course.objects.get(slug=old_slug)
                except Course.DoesNotExist:
                    raise CommandError(u"Course %s does not exist" % old_slug)
                try:
                    copy_course = Course.objects.get(slug=new_slug)
                except Course.DoesNotExist:
                    raise CommandError(u"Course %s does not exist" % new_slug)
                try:
                    user = User.objects.get(username=email)
                except Course.DoesNotExist:
                    raise CommandError(u"User %s does not exist" % email)
                clone_activiy_user_course(original_course, copy_course, user)
