# Copyright 2012 Rooter Analysis S.L.
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

from django.core.management.base import BaseCommand, CommandError

from moocng.courses.cache import invalidate_template_fragment
from moocng.courses.models import Course


class Command(BaseCommand):
    args = '<course_id course_id ...>'
    help = 'Invalidate the cached items related to the specified course'

    def handle(self, *args, **kwargs):

        if args:
            for course_id in args:
                try:
                    course = Course.objects.get(id=int(course_id))
                except Course.DoesNotExist:
                    raise CommandError('Course %s does not exist' % course_id)

                self._invalidate_course_cache(course)

        else:
            for course in Course.objects.all():
                self._invalidate_course_cache(course)

    def _invalidate_course_cache(self, course):
        self.stdout.write('Invalidating cache for %s\n' % course)

        invalidate_template_fragment('course_list')
        invalidate_template_fragment('course_overview_main_info', course.id)
        invalidate_template_fragment('course_overview_secondary_info', course.id)
