# -*- coding: utf-8 -*-
# Copyright 2014 UNED
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
from django import http
from django.template import RequestContext, loader
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def server_moocng_error(request, exception):
    status_code = exception.http_status_code
    t = loader.select_template(('%s.html' % status_code, 'http_error.html'))
    return http.HttpResponseGone(
        t.render(RequestContext(
            request,
            {'request_path': request.path,
             'title': exception.error_name,
             'message_exception': exception.message,
             'status_code': status_code})))
