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
from moocng.teacheradmin.decorators import is_teacher_or_staff
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.views import render_flatpage
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.utils import simplejson
from datetime import date
import requests
from jsonrpc_requests import Server, TransportError
import json
import sys
import base64

from moocng.badges.models import Award
from moocng.courses.models import Course, CourseTeacher, Announcement,KnowledgeQuantum
from moocng.courses.utils import (get_unit_badge_class, is_course_ready,
                                  is_teacher as is_teacher_test,
                                  send_mail_wrapper,get_sillabus_tree, create_groups,
                                  get_group_by_user_and_course, get_groups_by_course, change_user_group,
                                  create_kq_activity, update_course_mark_by_user, has_user_passed_course)

from moocng.courses.marks import get_course_mark, get_course_intermediate_calculations, normalize_unit_weight
from moocng.courses.security import (get_course_if_user_can_view_or_404,
                                     get_courses_available_for_user,
                                     get_units_available_for_user,
                                     get_related_courses_available_for_user,
                                     get_tasks_available_for_user,
                                     get_course_progress_for_user,
                                     get_course_rating_for_user,
                                     get_course_if_user_can_view_and_permission)
from moocng.courses.tasks import clone_activity_user_course_task
from moocng.courses.forms import CourseRatingForm, ForumPostForm, ForumReplyForm, ForumEditForm
from moocng.slug import unique_slugify
from moocng.communityshare.models import Microblog, Forum
from moocng.portal.templatetags.gravatar import gravatar_for_email
from moocng.utils import use_cache, generate_pdf

import hashlib
import time
from django.core import mail

from django.http import Http404
from django.template.loader import get_template
from django.template import Context
import xhtml2pdf.pisa as pisa
try:
    import StringIO
except Exception:
    from io import StringIO
import os

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

    institutions = settings.INSTITUTIONS

    return render_to_response(template, {
        'courses': courses,
        'use_cache': use_cache(request.user),
        'institutions': institutions
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
                except (User.MultipleObjectsReturned):
                    messages.error(request, _('There is more than a teacher with this name or email, please select other or contact with support.'))
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
        course_slug = unique_slugify(course, name)

        f = Forum()
        f.insert_forum_category(course.name, course_slug)
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
    course, permission = get_course_if_user_can_view_and_permission(course_slug, request)

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

    rating = course.get_rating()
    rating_obj = None
    if rating > 0:
        rating_obj = {}
        rating_obj['rating_loop'] = range(1,rating+1)
        rating_obj['empty_loop'] = range(rating+1,6)
    else:
        rating_obj = 0

    tasks = get_tasks_available_for_user(course, request.user)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/overview.html', {
        'course': course,
        'permission': permission,
        'progress': get_course_progress_for_user(course, request.user),
        'rating': get_course_rating_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'relatedcourses': relatedcourses,
        'organizers': organizers,
        'rating': rating_obj,
        'units': units,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'request': request,
        'course_teachers': course_teachers,
        'announcements': announcements,
        'use_old_calculus': settings.COURSES_USING_OLD_TRANSCRIPT,
        'is_overview' : True,
        'passed': has_passed,
    }, context_instance=RequestContext(request))


def course_classroom(request, course_slug):

    """
    Main view of the course content (class). If the user is not enrolled we
    show him a message. If the course is not ready and the user is not admin
    we redirect the user to a denied access page.

    :permissions: login
    :context: course, is_enrolled, ask_admin, unit_list, is_teacher, peer_view

    .. versionadded:: 0.1
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
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
            'status': u.status,
            'badge_class': get_unit_badge_class(u),
            'badge_tooltip': u.get_unit_type_name(),
        }
        units.append(unit)

    peer_review = {
        'text_max_size': settings.PEER_REVIEW_TEXT_MAX_SIZE,
        'file_max_size': settings.PEER_REVIEW_FILE_MAX_SIZE,
    }

    tasks = get_tasks_available_for_user(course, request.user)

    group = get_group_by_user_and_course(request.user.id, course.id)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/classroom.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'unit_list': units,
        'is_ready' : is_ready,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher_test(request.user, course),
        'peer_review': peer_review,
        'group': group,
        'passed': has_passed,
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
    m = Microblog()
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser :
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    peer_review = {
        'text_max_size': settings.PEER_REVIEW_TEXT_MAX_SIZE,
        'file_max_size': settings.PEER_REVIEW_FILE_MAX_SIZE,
    }

    tasks = get_tasks_available_for_user(course, request.user)

    announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]

    announcements = Announcement.objects.filter(course=course).order_by('datetime').reverse()[:5]

    CourseRatingFormSet = formset_factory(CourseRatingForm, extra=0, max_num=1)
    if request.method == "POST":
        rating_form = CourseRatingForm(request.POST)
        rating_formset = EvalutionCriteriaResponseFormSet(request.POST)
        if criteria_formset.is_valid() and submission_form.is_valid():
            # criteria_values = [(int(form.cleaned_data['evaluation_criterion_id']), int(form.cleaned_data['value'])) for form in criteria_formset]
            # try:
            #     review = save_review(assignment.kq, request.user, submitter, criteria_values, submission_form.cleaned_data['comments'])

            #     reviews = get_db().get_collection('peer_review_reviews')
            #     reviewed_count = reviews.find({
            #         'reviewer': user_id,
            #         'kq': assignment.kq.id
            #     }).count()
            #     on_peerreviewreview_created_task.apply_async(
            #         args=[review, reviewed_count],
            #         queue='stats',
            #     )

            #     current_site_name = get_current_site(request).name
            #     send_mail_to_submission_owner(current_site_name, assignment, review, submitter)
            # except IntegrityError:
            #     messages.error(request, _('Your can\'t submit two times the same review.'))
            #     return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

            # pending = assignment.minimum_reviewers - reviewed_count
            # if pending > 0:
            #     messages.success(request, _('Your review has been submitted. You have to review at least %d exercises more.') % pending)
            # else:
            #     messages.success(request, _('Your review has been submitted.'))
            # return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
            print 'ok'
    else:
        rating_form = CourseRatingForm()
        rating_formset = CourseRatingFormSet()

    group = get_group_by_user_and_course(request.user.id, course.id)
    posts_list = m.search_posts(course.hashtag, 0)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/dashboard.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'unit_list': get_sillabus_tree(course,request.user, True, True),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'next_task': tasks[2],
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'is_ready' : is_ready,
        'rating_form': rating_form,
        'rating_formset': rating_formset,
        'group': group,
        'announcements': announcements,
        'posts_list': posts_list,
        'passed': has_passed,
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
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/syllabus.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled' : is_enrolled,
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'unit_list': get_sillabus_tree(course,request.user,minversion=False),
        'group': group,
        'passed': has_passed,
    }, context_instance=RequestContext(request))

@login_required
def course_group(request, course_slug):
    m = Microblog()
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    tasks = get_tasks_available_for_user(course, request.user)

    groups = []
    group = {}
    group = get_group_by_user_and_course(request.user.id, course.id)

    if(group):
        groupsAux = get_groups_by_course(course.id, group["_id"])

        for g in groupsAux:
            if(len(g["members"]) <= course.group_max_size + (course.group_max_size * settings.GROUPS_UPPER_THRESHOLD / 100)):
                groups.append(g)

    posts_list = m.search_posts(group["hashtag"], 0)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/group.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled' : is_enrolled,
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'group': group,
        'groups':groups,
        'posts_list': posts_list,
        'passed': has_passed,
    }, context_instance=RequestContext(request))

@login_required
def course_forum(request, course_slug):
    f = Forum()
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            extra = {
                'geolocation': {
                    'lat': float(request.POST['context_geo_lat']),
                    'lon': float(request.POST['context_geo_lon'])
                },
                'course_slug': course_slug
            }
            f.insert_post(course_slug, request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postTitle'], form.cleaned_data['postText'], extra)
            return HttpResponseRedirect(reverse('course_forum', args=[course_slug]))
    else:
        course = get_course_if_user_can_view_or_404(course_slug, request)
        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        is_ready, ask_admin = is_course_ready(course)
        is_teacher = is_teacher_test(request.user, course)

        # if not is_ready and not request.user.is_superuser:
        if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
            return render_to_response('courses/no_content.html', {
                'course': course,
                'is_enrolled': is_enrolled,
                'ask_admin': ask_admin,
            }, context_instance=RequestContext(request))

        tasks = get_tasks_available_for_user(course, request.user)
        group = get_group_by_user_and_course(request.user.id, course.id)

        if is_enrolled:
            has_passed= has_user_passed_course(request.user, course)
        else:
            has_passed= False

        list_posts = f.get_posts(course.slug, 0)

        return render_to_response('courses/forum.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': tasks[0],
            'tasks_done': tasks[1],
            'is_enrolled' : is_enrolled,
            'is_ready' : is_ready,
            'is_teacher': is_teacher,
            'group': group,
            'passed': has_passed,
            'form': ForumPostForm(),
            'posts': list_posts,
        }, context_instance=RequestContext(request))

def course_forum_post(request, course_slug, post_id):
    f = Forum()
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            extra = {
                'geolocation': {
                    'lat': float(request.POST['context_geo_lat']),
                    'lon': float(request.POST['context_geo_lon'])
                },
                'course_slug': course_slug
            }
            f.save_reply(course_slug, post_id, request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postText'],extra)
            print form.cleaned_data["postText"]
            return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))
    else:
        course = get_course_if_user_can_view_or_404(course_slug, request)
        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        is_ready, ask_admin = is_course_ready(course)
        is_teacher = is_teacher_test(request.user, course)

        # if not is_ready and not request.user.is_superuser:
        if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
            return render_to_response('courses/no_content.html', {
                'course': course,
                'is_enrolled': is_enrolled,
                'ask_admin': ask_admin,
            }, context_instance=RequestContext(request))

        tasks = get_tasks_available_for_user(course, request.user)
        group = get_group_by_user_and_course(request.user.id, course.id)

        if is_enrolled:
            has_passed= has_user_passed_course(request.user, course)
        else:
            has_passed= False

        f = Forum()
        post = f.get_post_detail(post_id, request.user.id)
        if not post:
            raise Http404('Post not found')

        return render_to_response('courses/forum_post.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': tasks[0],
            'tasks_done': tasks[1],
            'is_enrolled' : is_enrolled,
            'is_ready' : is_ready,
            'is_teacher': is_teacher,
            'group': group,
            'passed': has_passed,
            'formReply': ForumReplyForm(),
            'formEdit': ForumEditForm(),
            'post': post,
        }, context_instance=RequestContext(request))

def course_forum_reply(request, course_slug, post_id, reply_id):
    f = Forum()
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            extra = {
                'geolocation': {
                    'lat': float(request.POST['context_geo_lat']),
                    'lon': float(request.POST['context_geo_lon'])
                },
                'course_slug': course_slug
            }
            reply_id = f.save_reply(course_slug, reply_id, request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postText'], extra)
            if reply_id is not False:
                return HttpResponseRedirect('{0}#{1}'.format(reverse('course_forum_post', args=[course_slug, post_id]), reply_id))
            else:
                return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))

def course_forum_vote(request, course_slug, post_id, reply_id, vote):
    f = Forum()
    try:
        geolocation = {
            'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
            'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
        }
    except:
        geolocation = {
            'lat': 0.0,
            'lon': 0.0
        }
    extra = {
        'geolocation': geolocation,
        'course_slug': course_slug
    }
    votes = f.post_vote(reply_id, request.user.id, vote, extra)
    return HttpResponse(simplejson.dumps(votes), mimetype='application/json')

def course_forum_post_flag(request, course_slug, post_id):
    f = Forum()
    success = f.post_flag(post_id, request.user.id)
    if success:
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))
    else:
        #TODO Alert: ERROR
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))

@is_teacher_or_staff
def course_forum_post_pin(request, course_slug, post_id):
    f = Forum()
    success = f.post_pin(post_id)
    if success:
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))
    else:
        #TODO Alert: ERROR
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))

def course_forum_post_edit(request, course_slug, post_id, reply_id):
    f = Forum()
    if request.method == 'POST':
        form = ForumEditForm(request.POST)
        if form.is_valid():
            success = f.post_edit(reply_id, request.user.id, course_slug, form.cleaned_data['postText'])
            if success:
                return HttpResponseRedirect('{0}#{1}'.format(reverse('course_forum_post', args=[course_slug, post_id]), reply_id))
            else:
                #TODO Alert: Can't edit
                return HttpResponseRedirect('{0}#{1}'.format(reverse('course_forum_post', args=[course_slug, post_id]), reply_id))

def course_forum_post_delete(request, course_slug, post_id):
    f = Forum()
    success = f.post_delete(post_id, request.user.id, course_slug, True)
    if success:
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))
    else:
        #TODO Alert: Can't delete
        return HttpResponseRedirect(reverse('course_forum_post', args=[course_slug, post_id]))

def course_forum_load_more(request, course_slug, page, query, search=False, hashtag=False):
    f = Forum()
    page = int(page)
    listPost = None
    if search and query:
        if hashtag:
            query = "#%s" % (query)
        listPost = f.search_posts(query, page)
    else:
        listPost = f.get_posts(course_slug, page)

    return render_to_response('courses/forum_post.html', {
            'request': request,
            'posts': listPost
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
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/calendar.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled' : is_enrolled,
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'group': group,
        'passed': has_passed,
    }, context_instance=RequestContext(request))

@login_required
def course_wiki(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    if not is_enrolled:
        messages.error(request, _('You are not enrolled in this course'))
        return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

    is_ready, ask_admin = is_course_ready(course)
    is_teacher = is_teacher_test(request.user, course)
    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)

    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/wiki.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled' : is_enrolled,
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'group': group,
        'passed': has_passed,
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

    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)
    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    # if not is_ready and not request.user.is_superuser:
    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': tasks[0],
            'tasks_done': tasks[1],
            'is_enrolled': is_enrolled,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    return render_to_response('courses/teachers.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled' : is_enrolled,
        'is_ready' : is_ready,
        'is_teacher': is_teacher,
        'group': group,
        'passed': has_passed,
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
    is_teacher = is_teacher_test(request.user, course)

    tasks = get_tasks_available_for_user(course, request.user)

    if not is_ready and not is_teacher and not request.user.is_staff and not request.user.is_superuser:
        return render_to_response('courses/no_content.html', {
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': tasks[0],
            'tasks_done': tasks[1],
            'is_enrolled': is_enrolled,
            'is_ready' : is_ready,
            'ask_admin': ask_admin,
        }, context_instance=RequestContext(request))

    units = []
    course_units = get_units_available_for_user(course, request.user, True)
    for u in course_units:
        unit = {
            'id': u.id,
            'title': u.title,
            'unittype': u.unittype,
            'badge_class': get_unit_badge_class(u),
            'badge_tooltip': u.get_unit_type_name(),
        }
        units.append(unit)

#####################################################################################
# TODO: Needs work to get the course score details
    total_mark, units_info = get_course_mark(course, request.user)
    total_weight_unnormalized, unit_course_counter, course_units = get_course_intermediate_calculations(course)

    for unit_info in units_info:
        print unit_info

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

    for unit_info in units_info_ordered:
        print unit_info
######################################################################################

    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)

    cert_url = None
    has_passed = has_user_passed_course(request.user, course)
    if(course.certification_available):
        print "Course threshold %s" % (course.threshold)
        if has_passed:
            if course.external_certification_available:
                cert_url = settings.CERTIFICATE_URL % {
                    'courseid': course.id,
                    'email': request.user.email.lower()
                }
            badge = course.completion_badge
            if badge is not None:
                try:
                    award = Award.objects.get(badge=badge, user=request.user)
                except Award.DoesNotExist:
                    award = Award(badge=badge, user=request.user)
                    award.save()

    print "course.external_certification_available = %s - certification_file = %s" % (course.external_certification_available, course.certification_file)

    return render_to_response('courses/progress.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'unit_list': units,
        'unit_list_info': units_info_ordered,
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'is_ready' : is_ready,
        'is_teacher': is_teacher_test(request.user, course),
        'group': group,
        'passed': has_passed,
        'cert_url': cert_url,
        'course_mark': round(total_mark,2),
    }, context_instance=RequestContext(request))


@login_required
def course_extra_info(request, course_slug):
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)
    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/static_page.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'is_teacher': is_teacher_test(request.user, course),
        'static_page': course.static_page,
        'group': group,
        'passed': has_passed,
    }, context_instance=RequestContext(request))


def announcement_detail(request, course_slug, announcement_id, announcement_slug):

    """
    Show a detail view of an announcement.

    :context: course, announcement

    .. versionadded:: 0.1
    """
    course = get_course_if_user_can_view_or_404(course_slug, request)
    announcement = get_object_or_404(Announcement, id=announcement_id)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_ready, ask_admin = is_course_ready(course)
    tasks = get_tasks_available_for_user(course, request.user)
    group = get_group_by_user_and_course(request.user.id, course.id)
    if is_enrolled:
        has_passed= has_user_passed_course(request.user, course)
    else:
        has_passed= False

    return render_to_response('courses/announcement.html', {
        'course': course,
        'progress': get_course_progress_for_user(course, request.user),
        'is_enrolled': is_enrolled,  # required due course nav templatetag
        'is_ready' : is_ready,
        'is_teacher': is_teacher_test(request.user, course),
        'group': group,
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'announcement': announcement,
        'template_base': 'courses/base_course.html',
        'group': group,
        'passed': has_passed,
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
        tasks = get_tasks_available_for_user(course, request.user)
        group = get_group_by_user_and_course(request.user.id, course.id)

        courses_info.append({
            'course': course,
            'progress': get_course_progress_for_user(course, request.user),
            'task_list': tasks[0],
            'tasks_done': tasks[1],
            'units_info': units_info_ordered,
            'mark': total_mark,
            'award': award,
            'passed': passed,
            'cert_url': cert_url,
            'use_old_calculus': use_old_calculus,
            'group': group,
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


@login_required
def create_course_groups(request,id):
    print "Create course groups id: %s" % (id)
    create_groups(id)
    return HttpResponse("true")

@login_required
def change_group(request, id_group, id_new_group):
    if request.method != 'POST':
        raise HttpResponseBadRequest
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    change_user_group(request.user.id, id_group, id_new_group, latitude, longitude)
    return HttpResponse("true")

@login_required
def check_survey(request, course_slug, survey_id, survey_token):
    user = request.user
    course = get_course_if_user_can_view_or_404(course_slug, request)
    units = get_units_available_for_user(course, user, True)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    tasks = get_tasks_available_for_user(course, request.user)
    is_teacher = is_teacher_test(user, course)
    is_ready, ask_admin = is_course_ready(course)
    group = get_group_by_user_and_course(request.user.id, course.id)

    try:
        server = Server(settings.SURVEY_API_URL, True)
        sessionKey = server.get_session_key(settings.SURVEY_API_USER, settings.SURVEY_API_PASSWORD)
        response = server.export_responses_by_token(sessionKey, survey_id, 'json', survey_token, 'es', 'complete')
        server.release_session_key(sessionKey)
    except TransportError as ex:
        return HttpResponse(ex.args[1])

    print "Response es %s" % (response)

    try:
        sliced = re.sub('<[^>]*>', '', response)
        decoded_response = json.loads(base64.b64decode(sliced))
        user_response = decoded_response[u'responses'][0]
        if user_response[user_response.keys()[0]][u'lastpage']:
            template_name = 'courses/survey_completed.html'

            last_unit = list(units)[-1]
            knowledge_quantums = KnowledgeQuantum.objects.filter(unit_id=last_unit.id)
            for kq in knowledge_quantums:
                create_kq_activity(kq, user)
            update_course_mark_by_user(course, user)

        else:
            template_name = 'courses/survey_not_completed.html'
    except Exception as ex:
        print ex
        template_name = 'courses/survey_not_completed.html'


    return render_to_response(template_name, {
        'course': course,
        'is_enrolled' : is_enrolled,
        'progress': get_course_progress_for_user(course, request.user),
        'task_list': tasks[0],
        'tasks_done': tasks[1],
        'is_teacher': is_teacher,
        'is_ready': is_ready,
        'group': group,
        'survey_token': survey_token,
        'survey_id': survey_id,
    }, context_instance=RequestContext(request))

@login_required
def course_diploma_pdf(request, course_slug):
    user = request.user
    course = get_course_if_user_can_view_or_404(course_slug, request)
    is_enrolled = course.students.filter(id=user.id).exists()
    is_teacher = is_teacher_test(user, course)
    is_ready, ask_admin = is_course_ready(course)
    if is_enrolled and has_user_passed_course(user, course):
        total_mark, units_info = get_course_mark(course, request.user)
        course_units = get_units_available_for_user(course, user)
        context_dict = {
            'pagesize': 'A4',
            'user': user,
            'course': course,
            'course_mark': round(total_mark,2),
            'course_units': course_units,
        }

        if hasattr(settings, 'MOOCNG_THEME') and 'diploma_template' in settings.MOOCNG_THEME:
            pdf = generate_pdf(request, 'diploma.html', context_dict)
        else:
            pdf = generate_pdf(request, 'courses/diploma.html', context_dict)

        if pdf:
            return HttpResponse(pdf.getvalue(), mimetype='application/pdf')
        else:
            return HttpResponse('Error while generating pdf')
    else:
        return HttpResponseForbidden()
