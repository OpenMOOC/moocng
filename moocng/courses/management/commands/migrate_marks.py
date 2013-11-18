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
from datetime import datetime

from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from moocng.api.tasks import update_kq_mark, update_unit_mark, update_course_mark
from moocng.mongodb import get_db


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user',
                    action='store',
                    dest='user',
                    default="",
                    help='User pk'),
    )

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):
        users = User.objects.all()
        if options["user"]:
            users = users.filter(pk=options["user"])
            if not users:
                raise CommandError(u"User %s does not exist" % options["user"])
            self.message("Migrating the user: %s" % users[0].username)
        else:
            first_day = datetime.strptime(settings.FIRST_DAY_MIGRATE_MARK, '%Y-%m-%d')
            today = datetime.today()
            num_days = (today - first_day).days
            start_pk = num_days * settings.NUM_MIGRATE_MARK_DAILY + 1
            end_pk = (num_days + 1) * settings.NUM_MIGRATE_MARK_DAILY
            self.message("Migrating the users from pk=%s to pk=%s " % (start_pk, end_pk))
            users = users.filter(pk__gte=start_pk, pk__lte=end_pk)
            if not users:
                #TODO: send email
                raise NotImplementedError
        db = get_db()
        for user in users:
            for course in user.courses_as_student.all():
                for unit in course.unit_set.scorables():
                    for kq in unit.knowledgequantum_set.all():
                        update_kq_mark(db, kq, user)
                    update_unit_mark(db, unit, user)
                update_course_mark(db, course, user)
