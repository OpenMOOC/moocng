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

from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.views import render_flatpage
from django.contrib.messages import success
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import (get_object_or_404, get_list_or_404,
                              render_to_response)
from django.template import RequestContext
from django.utils.translation import ugettext as _

from moocng.badges.models import Award
from moocng.courses.utils import calculate_course_mark
from moocng.courses.models import Course, Unit, Announcement


def home(request):
    courses = Course.objects.exclude(end_date__lt=date.today())
    return render_to_response('courses/home.html', {
            'courses': courses,
            }, context_instance=RequestContext(request))


def flatpage(request, page=""):
    # Translate flatpages
    lang = request.LANGUAGE_CODE.lower()
    fpage = get_object_or_404(FlatPage, url__exact=("/%s-%s/" % (page, lang)),
                              sites__id__exact=settings.SITE_ID)
    return render_flatpage(request, fpage)


def course_overview(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.user.is_authenticated():
        is_enrolled = course.students.filter(id=request.user.id).exists()
    else:
        is_enrolled = False

    if request.method == 'POST':
        if not is_enrolled:
            course.students.add(request.user)
            course.save()
            success(request,
                    _(u'Congratulations, you have successfully enroll in the course %(course)s')
                    % {'course': unicode(course)})
        else:
            course.students.remove(request.user)
            course.save()
            success(request,
                    _(u'You have successfully unenroll in the course %(course)s')
                    % {'course': unicode(course)})
        return HttpResponseRedirect(reverse('course_overview',
                                            args=(course.slug, )))

    announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]

    return render_to_response('courses/overview.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'request': request,
            'announcements': announcements,
            }, context_instance=RequestContext(request))


unit_badge_classes = {
    'n': 'badge-inverse',
    'h': 'badge-warning',
    'e': 'badge-important',
}


@login_required
def course_classroom(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    unit_list = get_list_or_404(Unit, course=course)

    units = []
    for u in unit_list:
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': unit_badge_classes[u.unittype],
        }
        units.append(unit)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        return HttpResponseForbidden(_('Your are not enrolled in this course'))

    return render_to_response('courses/classroom.html', {
        'course': course,
        'unit_list': units,
        'is_enrolled': is_enrolled,
    }, context_instance=RequestContext(request))


@login_required
def course_progress(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    unit_list = get_list_or_404(Unit, course=course)

    units = []
    for u in unit_list:
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': unit_badge_classes[u.unittype],
        }
        units.append(unit)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        return HttpResponseForbidden(_('Your are not enrolled in this course'))

    return render_to_response('courses/progress.html', {
        'course': course,
        'unit_list': units,
        'is_enrolled': is_enrolled, #required due course nav templatetag
    }, context_instance=RequestContext(request))


def announcement_detail(request, course_slug, announcement_slug):
    course = get_object_or_404(Course, slug=course_slug)
    announcement = get_object_or_404(Announcement, slug=announcement_slug)

    return render_to_response('courses/announcement.html', {
        'course': course,
        'announcement': announcement,
    }, context_instance=RequestContext(request))


@login_required
def transcript(request):
    course_list = request.user.courses_as_student.all()
    courses_info = []
    for course in course_list:
        total_mark, units_info = calculate_course_mark(course, request.user)
        award = None
        if course.threshold is not None and total_mark / 10 >= course.threshold:
            badge = course.completion_badge
            try:
                award = Award.objects.get(badge=badge, user=request.user)
            except Award.DoesNotExist:
                award = Award(badge=badge, user=request.user)
                award.save()
        courses_info.append({
            'course': course,
            'units_info': units_info,
            'mark': total_mark,
            'award': award,
        })
    return render_to_response('courses/transcript.html', {
        'courses_info': courses_info,
    }, context_instance=RequestContext(request))
