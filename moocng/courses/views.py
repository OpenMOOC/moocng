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
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.views import render_flatpage
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from moocng.badges.models import Award
from moocng.courses.models import Course, CourseTeacher, Announcement
from moocng.courses.utils import (calculate_course_mark, get_unit_badge_class,
                                  show_material_checker, is_course_ready,
                                  is_teacher as is_teacher_test)
from moocng.teacheradmin.utils import send_mail_wrapper


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


name_and_id_regex = re.compile('[^\(]+\((\d+)\)')


@login_required
def course_add(request):
    allow_public = False
    try:
        allow_public = settings.ALLOW_PUBLIC_COURSE_CREATION
    except AttributeError:
        pass

    if not allow_public and not request.user.is_staff:
        return HttpResponseForbidden(_("Only administrators can create courses"))

    if request.method == 'POST':
        if 'course_owner' in request.POST:
            email_or_id = request.POST['course_owner']
            try:
                validate_email(email_or_id)
                # is an email
                try:
                    owner = User.objects.get(email=email_or_id)
                except (User.DoesNotExist):
                    messages.error(request, _('That user doesn\'t exists, the owner must be an user of the platform'))
                    return HttpResponseRedirect(reverse('course_add'))
            except ValidationError:
                # is name plus id
                owner_id = name_and_id_regex.search(email_or_id)
                if owner_id is None:
                    messages.error(request, _('The owner must be a name plus ID or an email'))
                    return HttpResponseRedirect(reverse('course_add'))
                try:
                    owner_id = owner_id.groups()[0]
                    owner = User.objects.get(id=owner_id)
                except (User.DoesNotExist):
                    messages.error(request, _('That user doesn\'t exists, the owner must be an user of the platform'))
                    return HttpResponseRedirect(reverse('course_add'))
        else:
            owner = request.user

        name = request.POST['course_name']
        if (name == u''):
            messages.error(request, _('The name can\'t be an empty string'))
            return HttpResponseRedirect(reverse('course_add'))

        course = Course.objects.create(name=name, owner=owner,
                                       slug=slugify(name),
                                       description=_('To fill'))
        CourseTeacher.objects.create(course=course, teacher=owner)

        if not allow_public:
            subject = _('Your course "%s" has been created') % name
            message = _('Dear %(user)s\n\nYour course "%(course)s" has been created, and you have been assigned as the teacher owner. You can now access to the course administration interface and start adding content.\n\nBest regards,\n%(site)s\'s team') % {
                'user': owner.get_full_name(),
                'course': name,
                'site': get_current_site(request).name,
            }
            send_mail_wrapper(subject, message, [owner.email])

        messages.success(request, _('The course was successfully created'))
        return HttpResponseRedirect(reverse('teacheradmin_info', args=[course.slug]))

    return render_to_response('courses/add.html', {},
                              context_instance=RequestContext(request))


def course_overview(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    show_material = False
    if request.user.is_authenticated():
        is_enrolled = course.students.filter(id=request.user.id).exists()
        is_teacher = is_teacher_test(request.user, course)
        if is_enrolled:
            show_material = show_material_checker(course, request.user)
    else:
        is_enrolled = False
        is_teacher = False

    announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]

    return render_to_response('courses/overview.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'show_material': show_material,
        'is_teacher': is_teacher,
        'request': request,
        'announcements': announcements,
    }, context_instance=RequestContext(request))


@login_required
def course_classroom(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        return HttpResponseForbidden(_('You are not enrolled in this course'))

    is_ready, ask_admin = is_course_ready(course)

    if not is_ready:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
            'complaints_url': reverse('complaints'),
        }, context_instance=RequestContext(request))

    units = []
    for u in course.unit_set.all():
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': get_unit_badge_class(u),
        }
        units.append(unit)

    show_material = show_material_checker(course, request.user)
    if not show_material:
        return HttpResponseForbidden(_('You are enrolled in this course but it has not yet begun') + course.start_date.strftime(' (%d / %m / %Y)'))

    return render_to_response('courses/classroom.html', {
        'course': course,
        'unit_list': units,
        'is_enrolled': is_enrolled,
        'show_material': show_material,
        'is_teacher': is_teacher_test(request.user, course),
    }, context_instance=RequestContext(request))


@login_required
def course_progress(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        return HttpResponseForbidden(_('You are not enrolled in this course'))

    is_ready, ask_admin = is_course_ready(course)

    if not is_ready:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
            'complaints_url': reverse('complaints'),
        }, context_instance=RequestContext(request))

    units = []
    for u in course.unit_set.all():
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': get_unit_badge_class(u),
        }
        units.append(unit)

    show_material = show_material_checker(course, request.user)
    if not show_material:
        return HttpResponseForbidden(_('You are enrolled in this course but it has not yet begun') + course.start_date.strftime(' (%d / %m / %Y)'))

    return render_to_response('courses/progress.html', {
        'course': course,
        'unit_list': units,
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'show_material': show_material,
        'is_teacher': is_teacher_test(request.user, course),
    }, context_instance=RequestContext(request))


def announcement_detail(request, course_slug, announcement_id, announcement_slug):
    course = get_object_or_404(Course, slug=course_slug)
    announcement = get_object_or_404(Announcement, id=announcement_id)

    return render_to_response('courses/announcement.html', {
        'course': course,
        'announcement': announcement,
    }, context_instance=RequestContext(request))


@login_required
def transcript(request):
    course_list = request.user.courses_as_student.all()
    courses_info = []
    cert_url = ''
    for course in course_list:
        use_old_calculus = False
        if course.slug in settings.COURSES_USING_OLD_TRANSCRIPT:
            use_old_calculus = True
        total_mark, units_info = calculate_course_mark(course, request.user)
        award = None
        passed = False
        if course.threshold is not None and float(course.threshold) <= total_mark:
            passed = True
            cert_url = settings.CERTIFICATE_URL % {
                'courseid': course.id,
                'email': request.user.email
            }
            badge = course.completion_badge
            if badge is not None:
                try:
                    award = Award.objects.get(badge=badge, user=request.user)
                except Award.DoesNotExist:
                    award = Award(badge=badge, user=request.user)
                    award.save()
        for idx, uinfo in enumerate(units_info):
            unit_class = get_unit_badge_class(uinfo['unit'])
            units_info[idx]['badge_class'] = unit_class
            if not use_old_calculus and uinfo['unit'].unittype == 'n':
                units_info[idx]['hide'] = True
        courses_info.append({
            'course': course,
            'units_info': units_info,
            'mark': total_mark,
            'award': award,
            'passed': passed,
            'cert_url': cert_url,
        })
    return render_to_response('courses/transcript.html', {
        'courses_info': courses_info,
    }, context_instance=RequestContext(request))
