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

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import simplejson

from moocng.courses.models import Course
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.forms import CourseForm


@is_teacher_or_staff
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/stats.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/units.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_teachers(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/teachers.html', {
        'course': course,
        'request': request,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_teachers_invite(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    email_or_id = request.POST['data']
    user = None
    response = None

    try:
        validate_email(email_or_id)
        # is email
        try:
            user = User.objects.get(email=email_or_id)
        except User.DoesNotExist:
            pass
    except ValidationError:
        # is id
        try:
            user = User.objects.get(id=email_or_id)
        except (ValueError, User.DoesNotExist):
            response = HttpResponse(status=404)

    if user is not None:
        course.teachers.add(user)
        name = user.get_full_name()
        if not name:
            name = user.username
        data = {
            'id': user.id,
            'name': name,
            'pending': False
        }
        response = HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')
    elif response is None:
        # TODO invite email
        data = {
            'id': -1,
            'name': email_or_id,
            'pending': True
        }
        response = HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')

    return response


@is_teacher_or_staff
def teacheradmin_info(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    errors = ''
    success = False

    if request.method == 'POST':
        form = CourseForm(data=request.POST, instance=course)
        if form.is_valid():
            form.save()
            success = True
        else:
            errors = form.get_pretty_errors()

    return render_to_response('teacheradmin/info.html', {
        'course': course,
        'errors': errors,
        'success': success,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/announcements.html', {
        'course': course,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_emails(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('teacheradmin/emails.html', {
        'course': course,
    }, context_instance=RequestContext(request))
