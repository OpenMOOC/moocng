# Copyright 2013 Rooter Analysis S.L.
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
import ipdb

from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import (Course, CourseTeacher, Announcement, Unit,
                                   KnowledgeQuantum, Attachment, Question,
                                   Option)


class Command(BaseCommand):

    """
    Duplicate couses in the platform and their related content.

    Take in mind that this command is data model dependent. If the data model
    changes you'll need to take a look if still works properly. There are a
    lot of quirks with this, be careful and read the documentation before
    doing anything.
    """
    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    action='store_true',
                    dest='slug',
                    default=False,
                    help='Duplicate courses by slug'),
        make_option('--id',
                    action='store_true',
                    dest='id',
                    default=False,
                    help='Duplicate courses by ID'),
    )

    def _get_units(self, , old_course, course):
        """
        """
        self.stdout.write(" * Getting all the units in the course...")
        try:
            course_units = Unit.objects.filter(course=course)
        except:
            raise CommandError("Couln't obtain the course %s units." % course.name)
        try:
            for u in course_units:
                u.pk = None
                u.id = None
                u.course = course
                u.save()
        except:
            raise CommandError("Couldn't duplicate the course units.")
        
    def _duplicate_course(self, course):
        """
        Get the course object, the remove the PK and save, this will generate
        a new instance of the object. In this case we remove PK and ID due to
        the model inheritance.
        """
        self.stdout.write(" * Duplicating course and related content (may take a while)...\n")

        try:
            old_course = course
            # Asignate all the curernt content to new variables
            old_teachers = course.teachers
            old_owner = course.owner
            old_badge = course.completion_badge
        except:
            raise CommandError("Couldn't obtain the data for the course %s" % course.name)

        try:
            # First, set every object that doesn't depend on relations
            # Second, set every object that has relations
            # Third, set id and pk None and save
            ipdb.set_trace()
            course.teachers = old_teachers
            course.owner = old_owner
            course.completion_badge = old_badge
            course.pk = None
            course.id = None
            course.save()
        except:
            raise CommandError("Couldn't duplicate the course.\n")

    def _duplicate_course_by_slug(self, course_slug):
        c = Course.objects.get(slug=course_slug)
        self._duplicate_course(c)

    def _duplicate_course_by_id(self, course_id):
        c = Course.objects.get(id=course_id)
        self._duplicate_course(c)

    def handle(self, *args, **options):
        self.stdout.write('\n\n * Starting course duplication...\n')
        if options['slug']:
            for course_slug in args:
                self._duplicate_course_by_slug(course_slug)

        if options['id']:
            for course_id in args:
                self._duplicate_course_by_id(course_id)

        else:
            raise CommandError("You didn't select any option.")
