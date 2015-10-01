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

import pyprind

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db.models import Max

from moocng.courses.utils import update_course_mark_by_user


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user',
                    action='store',
                    dest='user',
                    default="",
                    help='User pk'),
        make_option('-c', '--courses',
                    action='store',
                    dest='courses_pks',
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

    def get_courses(self, user, courses_pks=None, courses_actives=False):
        courses_as_student = user.courses_as_student.all()
        if courses_pks:
            courses_pks = courses_pks.split(',')
            courses_as_student = courses_as_student.filter(pk__in=courses_pks)

        if courses_actives:
            courses_as_student = courses_as_student.actives()
        return courses_as_student

    def handle(self, *args, **options):
        users = User.objects.all()
        if options["user"]:
            users = users.filter(pk=options["user"])
            if not users:
                raise CommandError(u"User %s does not exist" % options["user"])
            self.message("Migrating the user: %s" % users[0].username)
        elif settings.NUM_MIGRATE_MARK_DAILY is not None:
            email_list = options["email_list"]
            if not email_list:
                raise CommandError(u"Please you have to pass the email list")
            first_day = datetime.strptime(settings.FIRST_DAY_MIGRATE_MARK, '%Y-%m-%d')
            today = datetime.today()
            num_days = (today - first_day).days
            start_pk = 1
            end_pk = (num_days + 1) * settings.NUM_MIGRATE_MARK_DAILY
            print "num_days: " + str(num_days)
            print "NUM_MIGRATE_MARK_DAILY: " + str(settings.NUM_MIGRATE_MARK_DAILY)
            self.message("Migrating the users from pk=%s to pk=%s " % (start_pk, end_pk))
            users = users.filter(pk__gte=start_pk, pk__lte=end_pk)
            max_pk = User.objects.aggregate(Max('pk'))['pk__max']
            if not users and end_pk >= max_pk:
                send_mail('The mark migration is finished',
                          'The mark migration is finished',
                          settings.DEFAULT_FROM_EMAIL,
                          email_list.split(','))
        courses_pks = options["courses_pks"]
        courses_actives = options["courses_actives"]
        bar = pyprind.ProgBar(users.count())
        for user in users:
            for course in self.get_courses(user, courses_pks, courses_actives):
                update_course_mark_by_user(course, user)
            bar.update()
