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

from django.core.urlresolvers import resolve

from tastypie.authorization import Authorization

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher


PERMISSIONS = {
    'get_courses_as_student': 'courses.can_list_allcourses',
    'get_passed_courses_as_student': 'courses.can_list_passedcourses'
}


class PublicReadTeachersModifyAuthorization(Authorization):

    def is_authorized(self, request, obj=None):
        if request.method == 'GET':
            return request.user.is_authenticated()
        else:
            return (request.user.is_authenticated() and
                    (is_teacher(request.user, Course.objects.all()) or
                     request.user.is_staff))


class TeacherAuthorization(Authorization):

    def is_authorized(self, request, obj=None):
        return (request.user.is_authenticated() and
                (is_teacher(request.user, Course.objects.all()) or
                 request.user.is_staff))


class ResourceAuthorization(Authorization):

    def is_authorized(self, request, obj=None):
        # Tasypie always return object = None
        # resources.py  function dispatch  422
        # TODO. Rewrite Tastypie to return get_obj()

        klass = self.resource_meta.object_class

        if klass and getattr(klass, '_meta', None):
            if request.method == 'GET':
                if obj:
                    permission_code = '%s.get_%s' % (klass._meta.app_label,
                        klass._meta.module_name)
                else:
                    permission_code = '%s.list_%s' % (klass._meta.app_label,
                        klass._meta.module_name)
            else:
                permission_codes = {
                    'POST': '%s.add_%s',
                    'PUT': '%s.change_%s',
                    'DELETE': '%s.delete_%s',
                }
                    # cannot map request method to permission code name
                if request.method in permission_codes:
                    permission_code = permission_codes[request.method] % (
                        klass._meta.app_label,
                        klass._meta.module_name)
            return request.user.has_perm(permission_code, obj)
        return False


class UserResourceAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        return object_list

    def read_detail(self, object_list, bundle):
        if bundle:
            #TODO owners and teachers should see user info
            has_get_permission = bundle.obj.id == bundle.request.user.id or  \
                             bundle.request.user.is_staff
            if not has_get_permission:
                url_name = resolve(bundle.request.path).url_name
                if url_name in PERMISSIONS.keys():
                    required_perm = PERMISSIONS.get(url_name)
                    return bundle.request.user.has_perm(required_perm)
                else:
                    # If can_list_allcourses then can get user info
                    return bundle.request.user.has_perm('courses.can_list_allcourses')
        return False

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        raise Unauthorized("You are not allowed to access that resource.")

    def update_list(self, object_list, bundle):
        return []

    def update_detail(self, object_list, bundle):
        raise Unauthorized("You are not allowed to access that resource.")

    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("You are not allowed to access that resource.")
