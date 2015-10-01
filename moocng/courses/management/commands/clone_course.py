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

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from moocng.courses.utils import clone_course


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='store',
                    dest='course',
                    default="",
                    help='Course pk to clone'),
    )

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):
        from moocng.courses.models import Course
        if not options["course"]:
            raise CommandError("--course / -c param is required")

        try:
            course = Course.objects.get(pk=options["course"])
        except Course.DoesNotExist:
            raise CommandError(u"Course %s does not exist" % options["course"])

        objs, file_path = clone_course(course, request=None)
        self.message("Created %s objects succesfully" % len(objs))
        self.message("The new course is pk=%s" % objs[0].pk)
        self.message("You have a trace in %s" % file_path)
