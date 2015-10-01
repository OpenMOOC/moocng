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

from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized

from moocng.api.models import UserApi
from moocng.courses.models import Course
from moocng.courses.utils import is_teacher


class DjangoAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

    def get_identifier(self, request):
        return request.user.username


class TeacherAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        return (is_teacher(request.user, Course.objects.all()) or request.user.is_staff)

    def get_identifier(self, request):
        return request.user.username


class ApiKeyAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        key = request.GET.get('key', None)
        if key:
            userapi = UserApi.objects.filter(key=key)
            if userapi:
                request.user = userapi[0].user
                return True
        return False

    def get_identifier(self, request):

        key = request.GET.get('key', None)
        if key:
            userapi = UserApi.objects.filter(key=key)
            if userapi:
                return userapi[0].user
        return 'nouser'


# TODO. This class belong tastypie 0.9.11
# (commit 5e8850434ef1c8672b0a22953bd7cc0def6347f8)
class MultiAuthentication(object):
    """
    An authentication backend that tries a number of backends in order.
    """
    def __init__(self, *backends, **kwargs):
        #super((MultiAuthentication, self).__init__(**kwargs))
        self.backends = backends

    def is_authenticated(self, request, **kwargs):
        """
        Identifies if the user is authenticated to continue or not.

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        unauthorized = False
        for backend in self.backends:
            check = backend.is_authenticated(request, **kwargs)
            if check:
                if isinstance(check, HttpUnauthorized):
                    unauthorized = unauthorized or check
                else:
                    request._authentication_backend = backend
                    unauthorized = check

        return unauthorized

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns a combination of IP address and hostname.
        """
        try:
            return request._authentication_backend.get_identifier(request)
        except AttributeError:
            return 'nouser'
