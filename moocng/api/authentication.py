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

# -*- coding: utf-8 -*-

from tastypie.authentication import Authentication

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher


class DjangoAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

    def get_identifier(self, request):
        return request.user.username


class TeacherAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        return is_teacher(request.user, Course.objects.all())

    def get_identifier(self, request):
        return request.user.username
