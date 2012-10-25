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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from moocng.courses.decorators import is_teacher
from moocng.courses.models import Course


@is_teacher
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/stats.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher
def teacheradmin_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/units.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher
def teacheradmin_teachers(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/teachers.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher
def teacheradmin_info(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/info.html', {
        'course': course,
    }, context_instance=RequestContext(request))


def teacheradmin_announcements(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/announcements.html', {
        'course': course,
    }, context_instance=RequestContext(request))


def teacheradmin_emails(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/emails.html', {
        'course': course,
    }, context_instance=RequestContext(request))
