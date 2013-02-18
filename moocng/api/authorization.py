# -*- coding: utf-8 -*-

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

from django.conf import settings
from django.http import HttpResponse

from tastypie.authorization import Authorization

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher


PERMISSIONS = {
    'get_courses': 'can_list_allcourses',
    'passed_courses': 'can_list_passedcourses'
}

class PublicReadTeachersModifyAuthorization(Authorization):

    def is_authorized(self, request, object=None):
        if request.method == 'GET':
            return request.user.is_authenticated()
        else:
            return (request.user.is_authenticated() and
                    (is_teacher(request.user, Course.objects.all()) or
                     request.user.is_staff))


class TeacherAuthorization(Authorization):

    def is_authorized(self, request, object=None):
        return (request.user.is_authenticated() and
                (is_teacher(request.user, Course.objects.all()) or
                 request.user.is_staff))


def check_permission(original_function=None):

    def decorated(resource, request, *args, **kwargs):
        if original_function.func_name in PERMISSIONS:
            required_perm = PERMISSIONS.get(original_function.func_name)
            if request.user.has_perm(required_perm):
                return original_function(resource, request, **kwargs)
        else:
            return HttpResponse("Unauthorized", status=401)

    return decorated
