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

from django.shortcuts import get_object_or_404

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher
from moocng.decorators import user_passes_test


def is_teacher_or_staff(original_function=None):

    def decorated(request, course_slug=None, *args, **kwargs):
        course = get_object_or_404(Course, slug=course_slug)

        def teacherness_test(user):
            return is_teacher(user, course) or user.is_staff

        decorator = user_passes_test(teacherness_test)

        return decorator(original_function)(request, course_slug,
                                            *args, **kwargs)

    return decorated
