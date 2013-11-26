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

from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Course
from moocng.courses.utils import clone_activity_user_course


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user',
                    action='store',
                    dest='user',
                    default="",
                    help='User pk'),
        make_option('-o', '--original-course',
                    action='store',
                    dest='original_course',
                    default="",
                    help='Original course pk'),
        make_option('-c', '--copy-course',
                    action='store',
                    dest='copy_course',
                    default="",
                    help='Copy course pk'),
    )

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):
        if not options["user"]:
            raise CommandError("--user / -u param is required")

        if not options["original_course"]:
            raise CommandError("--original-course / -o param is required")

        if not options["copy_course"]:
            raise CommandError("--copy-course / -c param is required")

        try:
            user = User.objects.get(pk=options["user"])
        except User.DoesNotExist:
            raise CommandError(u"User %s does not exist" % options["user"])

        try:
            original_course = Course.objects.get(pk=options["original_course"])
        except Course.DoesNotExist:
            raise CommandError(u"Course %s does not exist" % options["original_course"])

        try:
            copy_course = Course.objects.get(pk=options["copy_course"])
        except Course.DoesNotExist:
            raise CommandError(u"Course %s does not exist" % options["copy_course"])

        inserted_activity_rows, inserted_answer_rows, updated_answer_docs = clone_activity_user_course(user, copy_course, original_course)
        self.message('Cloned %s activity objects' % len(inserted_activity_rows))
        self.message('Cloned %s answer objects' % len(inserted_answer_rows))
        self.message('Updated %s answer objects' % len(updated_answer_docs))
