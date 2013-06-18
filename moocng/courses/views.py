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
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.generic import View

from moocng.badges.models import Award
from moocng.courses.models import Course, CourseTeacher, Announcement
from moocng.courses.utils import (get_unit_badge_class, is_course_ready,
                                  is_teacher as is_teacher_test,
                                  send_mail_wrapper)
from moocng.courses.marks import calculate_course_mark
from moocng.courses.security import (check_user_can_view_course,
                                     get_courses_available_for_user,
                                     get_units_available_for_user)
from django.template.defaultfilters import slugify


class HomeView(View):
    def get(self, request):
        use_cache = True
        if (request.user.is_superuser or request.user.is_staff or
                CourseTeacher.objects.filter(teacher=request.user.id).exists()):
            use_cache = False
        courses = get_courses_available_for_user(request.user)

        return render_to_response('courses/home.html', {
            'courses': courses,
            'use_cache': use_cache,
        }, context_instance=RequestContext(request))


class FlatPageView(View):
    def get(self, request, page=""):
        # Translate flatpages
        lang = request.LANGUAGE_CODE.lower()
        fpage = get_object_or_404(FlatPage, url__exact=("/%s-%s/" % (page, lang)),
                                  sites__id__exact=settings.SITE_ID)
        return render_flatpage(request, fpage)


class CourseAddView(View):
    name_and_id_regex = re.compile('[^\(]+\((\d+)\)')

    @method_decorator(login_required)
    def get(self, request):
        allow_public = getattr(settings, 'ALLOW_PUBLIC_COURSE_CREATION', False)

        if not allow_public and not request.user.is_staff:
            return HttpResponseForbidden(_("Only administrators can create courses"))

        return render_to_response('courses/add.html', {},
                                  context_instance=RequestContext(request))

    @method_decorator(login_required)
    def post(self, request):
        allow_public = getattr(settings, 'ALLOW_PUBLIC_COURSE_CREATION', False)

        if not allow_public and not request.user.is_staff:
            return HttpResponseForbidden(_("Only administrators can create courses"))

        owner = self.get_owner(request)
        if owner is None:
            return HttpResponseRedirect(reverse('course_add'))

        name = request.POST.get('course_name', '')
        if (name == u''):
            messages.error(request, _('The name can\'t be an empty string'))
            return HttpResponseRedirect(reverse('course_add'))

        course = Course(name=name, owner=owner, description=_('To fill'))
        course.slug = slugify(course)
        course.save()

        CourseTeacher.objects.create(course=course, teacher=owner)

        if not allow_public:
            self.notify_creation(get_current_site(request), name, owner)

        messages.success(request, _('The course was successfully created'))
        return HttpResponseRedirect(reverse('teacheradmin_info', args=[course.slug]))

    def notify_creation(self, site, name, owner):
        subject = _('Your course "%s" has been created') % name
        template = 'courses/email_new_course.txt'
        context = {
            'user': owner.get_full_name(),
            'course': name,
            'site': site.name
        }
        to = [owner.email]
        send_mail_wrapper(subject, template, context, to)

    def get_owner(self, request):
        owner = None

        if 'course_owner' in request.POST:
            email_or_id = request.POST['course_owner']
            try:
                validate_email(email_or_id)
                # is an email
                try:
                    owner = User.objects.get(email=email_or_id)
                except (User.DoesNotExist):
                    messages.error(request, _('That user doesn\'t exists, the owner must be an user of the platform'))
            except ValidationError:
                # is name plus id
                owner_id = self.name_and_id_regex.search(email_or_id)
                if owner_id is None:
                    messages.error(request, _('The owner must be a name plus ID or an email'))
                try:
                    owner_id = owner_id.groups()[0]
                    owner = User.objects.get(id=owner_id)
                except (User.DoesNotExist):
                    messages.error(request, _('That user doesn\'t exists, the owner must be an user of the platform'))
        else:
            owner = request.user

        return owner


class CourseOverviewView(View):
    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        check_user_can_view_course(course, request)

        if request.user.is_authenticated():
            is_enrolled = course.students.filter(id=request.user.id).exists()
            is_teacher = is_teacher_test(request.user, course)
        else:
            is_enrolled = False
            is_teacher = False

        course_teachers = CourseTeacher.objects.filter(course=course)
        announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]
        units = get_units_available_for_user(course, request.user, True)
        use_old_calculus = course.slug in settings.COURSES_USING_OLD_TRANSCRIPT

        return render_to_response('courses/overview.html', {
            'course': course,
            'units': units,
            'is_enrolled': is_enrolled,
            'is_teacher': is_teacher,
            'request': request,
            'course_teachers': course_teachers,
            'announcements': announcements,
            'use_old_calculus': use_old_calculus,
        }, context_instance=RequestContext(request))


class CourseClassroomProgressBaseView(View):
    def get_context_data(self, request, course, peer_review=False):
        is_ready, ask_admin = is_course_ready(course)
        is_enrolled = course.students.filter(id=request.user.id).exists()

        context = {
            'course': course,
            'is_enrolled': is_enrolled,
        }

        if is_ready:
            units = self.get_units(course, request.user)
            context['unit_list'] = units
            context['is_teacher'] = is_teacher_test(request.user, course)
        else:
            context['ask_admin'] = ask_admin

        if peer_review:
            context['peer_review'] = {
                'text_max_size': settings.PEER_REVIEW_TEXT_MAX_SIZE,
                'file_max_size': settings.PEER_REVIEW_FILE_MAX_SIZE,
            }

        return context

    def get_units(self, course, user):
        units = []
        for u in get_units_available_for_user(course, user):
            unit = {
                'id': u.id,
                'title': u.title,
                'unittype': u.unittype,
                'badge_class': get_unit_badge_class(u),
                'badge_tooltip': u.get_unit_type_name(),
            }
            units.append(unit)

        return units

class CourseClassroomView(CourseClassroomProgressBaseView):
    @method_decorator(login_required)
    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        return render_to_response(
            self.get_template_name(course),
            self.get_context_data(request, course, peer_review=True),
            context_instance=RequestContext(request)
        )

    def get_template_name(self, course):
        is_ready, ask_admin = is_course_ready(course)
        if is_ready:
            return 'courses/classroom.html'
        else:
            return 'courses/no_content.html'


class CourseProgressView(CourseClassroomProgressBaseView):
    @method_decorator(login_required)
    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        return render_to_response(
            self.get_template_name(course),
            self.get_context_data(request, course),
            context_instance=RequestContext(request)
        )

    def get_template_name(self, course):
        is_ready, ask_admin = is_course_ready(course)
        if is_ready:
            return 'courses/progress.html'
        else:
            return 'courses/no_content.html'


class AnnouncementDetailView(View):
    def get(self, request, course_slug, announcement_id, announcement_slug):
        course = get_object_or_404(Course, slug=course_slug)
        announcement = get_object_or_404(Announcement, id=announcement_id)

        return render_to_response('courses/announcement.html', {
            'course': course,
            'announcement': announcement,
        }, context_instance=RequestContext(request))


class TranscriptView(View):
    @method_decorator(login_required)
    def get(self, request):
        course_list = request.user.courses_as_student.all()
        courses_info = self.get_courses_info(request, course_list)

        return render_to_response('courses/transcript.html', {
            'courses_info': courses_info,
        }, context_instance=RequestContext(request))

    def get_courses_info(self, request, course_list):
        courses_info = []
        for course in course_list:
            cert_url = settings.CERTIFICATE_URL % {
                'courseid': course.id,
                'email': request.user.email.lower()
            }
            use_old_calculus = course.slug in settings.COURSES_USING_OLD_TRANSCRIPT

            total_mark, units_info = calculate_course_mark(course, request.user)

            passed = self.has_passed_course(course, total_mark)

            award = None
            if passed:
                award = self.get_award(course)

            self.complete_units_info(units_info, use_old_calculus)

            courses_info.append({
                'course': course,
                'units_info': units_info,
                'mark': total_mark,
                'award': award,
                'passed': passed,
                'cert_url': cert_url,
                'use_old_calculus': use_old_calculus,
            })

    def has_passed_course(self, course, total_mark):
        return course.threshold is not None and float(course.threshold) <= total_mark

    def get_award(self, course):
        award = None
        if course.completion_badge is not None:
            try:
                award = Award.objects.get(badge=badge, user=request.user)
            except Award.DoesNotExist:
                award = Award(badge=badge, user=request.user)
                award.save()
        return award

    def complete_units_info(self, units_info, use_old_calculus):
        for idx, uinfo in enumerate(units_info):
            unit_class = get_unit_badge_class(uinfo['unit'])
            units_info[idx]['badge_class'] = unit_class
            if (not use_old_calculus and uinfo['unit'].unittype == 'n') or \
                    not units_info[idx]['use_unit_in_total']:
                units_info[idx]['hide'] = True
