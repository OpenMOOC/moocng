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
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from datetime import date

from moocng.badges.models import Award
from moocng.courses.models import Course, CourseTeacher, Announcement,KnowledgeQuantum
from moocng.courses.utils import (get_unit_badge_class, is_course_ready,
                                  is_teacher as is_teacher_test,
                                  send_mail_wrapper,get_sillabus_tree)
from moocng.courses.marks import get_course_mark, get_course_intermediate_calculations, normalize_unit_weight
from moocng.courses.security import (get_course_if_user_can_view_or_404,
                                     get_courses_available_for_user,
                                     get_units_available_for_user,
                                     get_related_courses_available_for_user,
                                     get_tasks_available_for_user,
                                     get_course_progress_for_user)
from moocng.courses.tasks import clone_activity_user_course_task
from moocng.slug import unique_slugify
from moocng.utils import use_cache


def home(request):

    """
    Home view for the courses. This view will show a list of all the available
    courses in the platform if they're published, unless the user is is_superuser
    in which case we show everything (check **get_courses_available_for_user()**)

    :context: courses, use_cache
    .. versionadded:: 0.1
    """
    courses = get_courses_available_for_user(request.user)

    if hasattr(settings, 'COURSE_SHOW_AS_LIST'):
        show_as_list = settings.COURSE_SHOW_AS_LIST
        if show_as_list:
            template = 'courses/home_as_list.html'
        else:
            template = 'courses/home_as_grid.html'
            courses = grouper(courses, 3)
    else:
        template = 'courses/home_as_list.html'

    return render_to_response(template, {
        'courses': courses,
        'use_cache': use_cache(request.user),
    }, context_instance=RequestContext(request))


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    from itertools import izip_longest
    return izip_longest(fillvalue=fillvalue, *args)


def flatpage(request, page=""):

    """
    Function for translating flatpages. This function picks up the pagename
    followed by a dash and the language code. If it's not found it returns
    a 404.

    .. versionadded:: 0.1
    """
    # Translate flatpages
    lang = request.LANGUAGE_CODE.lower()
    fpage = get_object_or_404(FlatPage, url__exact=("/%s-%s/" % (page, lang)),
                              sites__id__exact=settings.SITE_ID)
    return render_flatpage(request, fpage)


name_and_id_regex = re.compile('[^\(]+\((\d+)\)')


@login_required
def course_add(request):

    """
    Create new courses. By default courses are created by platform admins unless
    ALLOW_PUBLIC_COURSE_CREATION is set to True.

    The view validates the email of the course_owner field and the course_name
    unless a regular user is creating the course, in which case the course_owner
    is directly taken from the current user.

    After that the course name is slugified and the CourseTeacher and Course are
    saved, and the user is returned to the TeacherAdmin module.

    .. versionadded:: 0.1
    """
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

        course = Course(name=name, owner=owner, description=_('To fill'))
        unique_slugify(course, name)
        course.save()

        CourseTeacher.objects.create(course=course, teacher=owner)

        if not allow_public:
            subject = _('Your course "%s" has been created') % name
            template = 'courses/email_new_course.txt'
            context = {
                'user': owner.get_full_name(),
                'course': name,
                'site': get_current_site(request).name
            }
            to = [owner.email]
            send_mail_wrapper(subject, template, context, to)

        messages.success(request, _('The course was successfully created'))
        return HttpResponseRedirect(reverse('teacheradmin_info',
                                            args=[course.slug]))

    return render_to_response('courses/add.html', {},
                              context_instance=RequestContext(request))


def course_overview(request, course_slug):

    """
    Show the course main page. This will show the main information about the
    course and the 'register to this course' button.

    .. note:: **use_old_calculus** is a compatibility method with old evaluation
              methods, which allowed the normal units to be evaluated. The new
              system does not evaluate normal units, only tasks and exams.

    :context: course, units, is_enrolled, is_teacher, request, course_teachers,
              announcements, use_old_calculus

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)
    
    relatedcourses = get_related_courses_available_for_user(course, request.user)

    if request.user.is_authenticated():
        is_enrolled = course.students.filter(id=request.user.id).exists()
        is_teacher = is_teacher_test(request.user, course)
    else:
        is_enrolled = False
        is_teacher = False

    course_teachers = CourseTeacher.objects.filter(course=course)
    
    organizers = []
    for teacher in course_teachers:
        organization = teacher.teacher.get_profile().organization.all()

        for v in organization:            
            if(v not in organizers):
                organizers.append(v)

    #course_has_started = True if date.today() >= course.start_date else False
    announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]
    units = get_units_available_for_user(course, request.user, True)
    
    # Rating is dummy right now
    rating = {}
    if course.user_score:
        rating['rating_loop'] = range(1,course.user_score+1)
        rating['empty_loop'] = range(course.user_score+1,6)

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/overview.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'relatedcourses': relatedcourses,
        'organizers': organizers,
        'rating': rating,
        'units': units,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'request': request,
        'course_teachers': course_teachers,
        'announcements': announcements,
        'use_old_calculus': settings.COURSES_USING_OLD_TRANSCRIPT,
        'is_overview' : True
    }, context_instance=RequestContext(request))

@login_required
def course_classroom(request, course_slug):

    """
    Main view of the course content (class). If the user is not enrolled we
    show him a message. If the course is not ready and the user is not admin
    we redirect the user to a denied access page.

    :permissions: login
    :context: course, is_enrolled, ask_admin, unit_list, is_teacher, peer_view

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)

    if not is_ready and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    units = []
    for u in get_units_available_for_user(course, request.user):
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': get_unit_badge_class(u),
            'badge_tooltip': u.get_unit_type_name(),
        }
        units.append(unit)

    peer_review = {
        'text_max_size': settings.PEER_REVIEW_TEXT_MAX_SIZE,
        'file_max_size': settings.PEER_REVIEW_FILE_MAX_SIZE,
    }

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/classroom.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'unit_list': units,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher_test(request.user, course),
        'peer_review': peer_review
    }, context_instance=RequestContext(request))

@login_required
def course_dashboard(request, course_slug):

    """
    Main view of the course content (class). If the user is not enrolled we
    show him a message. If the course is not ready and the user is not admin
    we redirect the user to a denied access page.

    :permissions: login
    :context: course, is_enrolled, ask_admin, unit_list, is_teacher, peer_view

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher :
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    peer_review = {
        'text_max_size': settings.PEER_REVIEW_TEXT_MAX_SIZE,
        'file_max_size': settings.PEER_REVIEW_FILE_MAX_SIZE,
    }

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/dashboard.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'unit_list': get_sillabus_tree(course,request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'is_ready' : is_ready,
    }, context_instance=RequestContext(request))

@login_required
def course_setmark(request,knowledgequantumid):
    kq = get_object_or_404(KnowledgeQuantum,pk=knowledgequantumid)
    kq.set_as_current(request.user)
    return HttpResponse(kq.title)

@login_required
def course_syllabus(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/syllabus.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled' : is_enrolled,   
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'unit_list': get_sillabus_tree(course,request.user,minversion=False)
    }, context_instance=RequestContext(request))

@login_required
def course_team(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/team.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled' : is_enrolled,   
        'is_ready' : is_ready,
        'is_teacher': is_teacher,

    }, context_instance=RequestContext(request))

@login_required
def course_forum(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/forum.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled' : is_enrolled,  
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
    }, context_instance=RequestContext(request))

@login_required
def course_calendar(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)
    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/calendar.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled' : is_enrolled,   
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
    }, context_instance=RequestContext(request))

@login_required
def course_teachers(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': task_list,
            'tasks_done': tasks_done,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    return render_to_response('courses/teachers.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled' : is_enrolled,   
        'is_ready' : is_ready,
        'is_teacher': is_teacher
    }, context_instance=RequestContext(request))

@login_required
def course_progress(request, course_slug):

    """
    Main view for the user progress in the course. This will return the units for
    the user in the current course.

    :permissions: login
    :context: course, is_enrolled, ask_admin, course, unit_list, is_teacher

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)

    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    if not is_ready:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': task_list,
            'tasks_done': tasks_done,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    units = []
    for u in get_units_available_for_user(course, request.user):
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': get_unit_badge_class(u),
            'badge_tooltip': u.get_unit_type_name(),
        }
        units.append(unit)

    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/progress.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'unit_list': units,
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'is_teacher': is_teacher_test(request.user, course),
    }, context_instance=RequestContext(request))


@login_required
def course_extra_info(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/static_page.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'is_teacher': is_teacher_test(request.user, course),
        'static_page': course.static_page,
    }, context_instance=RequestContext(request))


def announcement_detail(request, course_slug, announcement_id, announcement_slug):

    """
    Show a detail view of an announcement.

    :context: course, announcement

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)
    announcement = get_object_or_404(Announcement, id=announcement_id)
    task_list, tasks_done = get_tasks_available_for_user(course, request.user)

    return render_to_response('courses/announcement.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': task_list,
        'tasks_done': tasks_done,
        'announcement': announcement,
        'template_base': 'courses/base_course.html'
    }, context_instance=RequestContext(request))


@login_required
def transcript(request, course_slug=None):
    user = request.user
    course_list = user.courses_as_student.all()
    course_transcript = None
    template_name = 'courses/transcript.html'
    if course_slug:
        template_name = 'courses/transcript_course.html'
        course_transcript = get_object_or_404(Course, slug=course_slug)
        course_list = course_list.filter(slug=course_slug)
    courses_info = []
    use_old_calculus = settings.COURSES_USING_OLD_TRANSCRIPT
    for course in course_list:
        cert_url = ''
        total_mark, units_info = get_course_mark(course, user)
        award = None
        passed = False
        if course.threshold is not None and float(course.threshold) <= total_mark:
            passed = True
            cert_url = settings.CERTIFICATE_URL % {
                'courseid': course.id,
                'email': user.email.lower()
            }
            badge = course.completion_badge
            if badge is not None:
                try:
                    award = Award.objects.get(badge=badge, user=user)
                except Award.DoesNotExist:
                    award = Award(badge=badge, user=user)
                    award.save()
        total_weight_unnormalized, unit_course_counter, course_units = get_course_intermediate_calculations(course)

        units_info_ordered = []
        for unit in course_units:
            uinfo = next((u for u in units_info if u['unit_id'] == unit.pk),
                         {'relative_mark': 0, 'mark': 0})
            uinfo['unit'] = unit
            normalized_unit_weight = normalize_unit_weight(unit,
                                                           unit_course_counter,
                                                           total_weight_unnormalized)
            uinfo['normalized_weight'] = normalized_unit_weight
            unit_class = get_unit_badge_class(unit)
            uinfo['badge_class'] = unit_class
            units_info_ordered.append(uinfo)
        task_list, tasks_done = get_tasks_available_for_user(course, request.user)
        
        courses_info.append({
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': task_list,
            'tasks_done': tasks_done,
            'units_info': units_info_ordered,
            'mark': total_mark,
            'award': award,
            'passed': passed,
            'cert_url': cert_url,
            'use_old_calculus': use_old_calculus,
        })
    return render_to_response(template_name, {
        'courses_info': courses_info,
        'course_transcript': course_transcript,
    }, context_instance=RequestContext(request))


@login_required
def clone_activity(request, course_slug):
    if request.method != 'POST':
        raise HttpResponseBadRequest
    user = request.user
    course = get_course_if_user_can_view_or_404(course_slug, request)
    course_student_relation = get_object_or_404(user.coursestudent_set, course=course)
    if not course_student_relation.can_clone_activity():
        return HttpResponseBadRequest()
    course_student_relation.old_course_status = 'c'
    course_student_relation.save()
    clone_activity_user_course_task.apply_async(args=[user, course, get_language()],
                                                queue='courses')
    message = _(u'We are cloning the activity from %(course)s. You will receive an email soon')
    messages.success(request,
                     message % {'course': unicode(course)})
    return HttpResponseRedirect(course.get_absolute_url())
