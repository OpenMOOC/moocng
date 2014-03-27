# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

from django.core.urlresolvers import resolve

from tastypie.authorization import Authorization

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher


PERMISSIONS = {
    'get_courses_as_student': 'courses.can_list_allcourses',
    'get_passed_courses_as_student': 'courses.can_list_passedcourses'
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


class UserResourceAuthorization(Authorization):

    def is_authorized(self, request, object=None):
        # We check if the method is GET here instead of relaying in the
        # tastypie allowed_methods property because of the overrided urls,
        # those ignore the allowed_methods restriction
        if request.method == 'GET':
            url_name = resolve(request.path).url_name
            if url_name in PERMISSIONS.keys():
                required_perm = PERMISSIONS.get(url_name)
                return request.user.has_perm(required_perm)
            return True
        return False
