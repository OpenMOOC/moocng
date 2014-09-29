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

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils import simplejson
from django.utils.translation import ugettext as _

from moocng.courses.models import (Course, CourseTeacher, KnowledgeQuantum,
                                   Option, Announcement, Unit, Attachment)
from moocng.courses.utils import UNIT_BADGE_CLASSES
from moocng.categories.models import Category
from moocng.media_contents import get_media_content_types_choices
from moocng.mongodb import get_db
from moocng.portal.templatetags.gravatar import gravatar_img_for_email
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.forms import (CourseForm, AnnouncementForm,
                                       MassiveEmailForm, AssetTeacherForm,
                                       StaticPageForm)
from moocng.teacheradmin.models import Invitation, MassiveEmail
from moocng.teacheradmin.tasks import send_massive_email_task
from moocng.teacheradmin.utils import (send_invitation,
                                       send_removed_notification)
from moocng.videos.tasks import process_video_task

from moocng.assets.utils import course_get_assets
from moocng.assets.models import Asset
from moocng.externalapps.models import externalapps

import pprint


@is_teacher_or_staff
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    stats_course = get_db().get_collection('stats_course')
    stats = stats_course.find_one({'course_id': course.id})

    if stats is not None:
        data = {
            'enrolled': course.students.count(),
            'started': stats.get('started', -1),
            'completed': stats.get('completed', -1),
        }

        if course.threshold is not None:
            #if the course doesn't support certification, then don't return the
            #'passed' stat since it doesn't apply
            data['passed'] = stats.get('passed', -1)

        return render_to_response('teacheradmin/stats.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'initial_data': simplejson.dumps(data),
        }, context_instance=RequestContext(request))
    else:
        messages.error(request, _(u"There are no statistics for this course."))
        return HttpResponseRedirect(reverse('teacheradmin_info',
                                            args=[course_slug]))


@is_teacher_or_staff
def teacheradmin_stats_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    stats_unit = get_db().get_collection('stats_unit')
    data = []

    for unit in course.unit_set.only('id', 'title').all():
        stats = stats_unit.find_one({'unit_id': unit.id})

        if stats is not None:
            unit_data = {
                'id': unit.id,
                'title': unit.title,
                'started': stats.get('started', -1),
                'completed': stats.get('completed', -1),
            }

            if course.threshold is not None:
                # if the course doesn't support certification, then don't return
                # the 'passed' stat since it doesn't apply
                unit_data['passed'] = stats.get('passed', -1)

            data.append(unit_data)

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_stats_kqs(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not 'unit' in request.GET:
        return HttpResponse(status=400)
    unit = get_object_or_404(Unit, id=request.GET['unit'])
    if not unit in course.unit_set.all():
        return HttpResponse(status=400)
    stats_kq = get_db().get_collection('stats_kq')
    data = []

    for kq in unit.knowledgequantum_set.only('id', 'title').all():
        stats = stats_kq.find_one({'kq_id': kq.id})

        if stats is not None:
            kq_data = {
                'id': kq.id,
                'title': kq.title,
                'viewed': stats.get('viewed', 1)
            }

            kq_type = kq.kq_type()
            if kq_type == 'PeerReviewAssignment':
                kq_data['submitted'] = stats.get('submitted', -1)
                kq_data['reviews'] = stats.get('reviews', -1)
                kq_data['reviewers'] = stats.get('reviewers', -1)
            elif kq_type == 'Question':
                kq_data['submitted'] = stats.get('submitted', -1)

            if course.threshold is not None:
                # if the course doesn't support certification, then don't
                # return the 'passed' stat since it doesn't apply
                kq_data['passed'] = stats.get('passed', -1)

            data.append(kq_data)

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/units.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'unit_badge_classes': simplejson.dumps(UNIT_BADGE_CLASSES),
        'media_content_type_choices': get_media_content_types_choices(),
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units_forcevideoprocess(request, course_slug):
    if not 'kq' in request.GET:
        return HttpResponse(status=400)
    kq = get_object_or_404(KnowledgeQuantum, id=request.GET['kq'])

    question_list = kq.question_set.all()
    if len(question_list) > 0:
        process_video_task.delay(question_list[0].id)
    return HttpResponse()


@is_teacher_or_staff
def teacheradmin_units_attachment(request, course_slug):
    if request.method == 'POST':
        if not 'kq' in request.GET:
            return HttpResponse(status=400)
        kq = get_object_or_404(KnowledgeQuantum, id=request.GET['kq'])

        if not('attachment' in request.FILES.keys()):
            return HttpResponse(status=400)

        uploaded_file = request.FILES['attachment']
        attachment = Attachment(attachment=uploaded_file, kq=kq)
        attachment.save()

        return HttpResponse()

    elif request.method == 'DELETE':
        if not 'attachment' in request.GET:
            return HttpResponse(status=400)

        attachment = get_object_or_404(Attachment,
                                       id=request.GET['attachment'])
        attachment.delete()

        return HttpResponse()

    else:
        return HttpResponse(status=400)


@is_teacher_or_staff
def teacheradmin_units_question(request, course_slug, kq_id):
    kq = get_object_or_404(KnowledgeQuantum, id=kq_id)
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    question_list = kq.question_set.all()
    if len(question_list) > 0:
        obj = question_list[0]
    else:
        return HttpResponse(status=400)

    if 'HTTP_REFERER' in request.META:
        goback = request.META['HTTP_REFERER']
    else:
        goback = None

    if obj is None:
        raise Http404(_('The KQ with the %s id doesn\'t exists') % kq_id)

    if request.method == 'POST':
        data = simplejson.loads(request.raw_post_data)
        option = obj.option_set.create(**data)
        data['id'] = option.id
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')
    else:
        json = [{
                'id': opt.id,
                'optiontype': opt.optiontype,
                'solution': opt.solution,
                'feedback': opt.feedback,
                'text': opt.text,
                'x': opt.x, 'y': opt.y,
                'width': opt.width, 'height': opt.height,
                } for opt in obj.option_set.all()]
        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'object_id': obj.id,
            'original': obj,
            'options_json': simplejson.dumps(json),
            'goback': goback,
        }
        return render_to_response('teacheradmin/question.html', context,
                                  context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units_option(request, course_slug, kq_id, option_id):
    option = get_object_or_404(Option, id=option_id)

    if request.method == 'PUT':
        data = simplejson.loads(request.raw_post_data)
        for key, value in data.items():
            if key != 'id':
                setattr(option, key, value)
        option.save()
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')

    elif request.method == 'DELETE':
        option.delete()
        return HttpResponse('')

    elif request.method == 'GET':
        data = {
            'id': option.id,
            'optiontype': option.optiontype,
            'solution': option.solution,
            'feedback': option.feedback,
            'text': option.text,
            'x': option.x, 'y': option.y,
            'width': option.width, 'height': option.height,
        }
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_teachers(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/teachers.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'course_teachers': CourseTeacher.objects.filter(course=course),
        'invitations': Invitation.objects.filter(course=course),
        'request': request,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_teachers_delete(request, course_slug, email_or_id):
    course = get_object_or_404(Course, slug=course_slug)
    response = HttpResponse()

    try:
        validate_email(email_or_id)
        # is email, so is an invitation
        try:
            invitation = Invitation.objects.get(email=email_or_id,
                                                course=course)
            invitation.delete()
            send_removed_notification(request, email_or_id, course)
        except Invitation.DoesNotExist:
            response = HttpResponse(status=404)
    except ValidationError:
        # is an id
        try:
            ct = CourseTeacher.objects.get(id=email_or_id)
            if ct.teacher == course.owner:
                response = HttpResponse(status=401)
            else:
                ct.delete()
                send_removed_notification(request, ct.teacher.email, course)
        except (ValueError, CourseTeacher.DoesNotExist):
            response = HttpResponse(status=404)

    return response


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
        try:
            ct = CourseTeacher.objects.get(course=course, teacher=user)
            return HttpResponse(status=409)
        except CourseTeacher.DoesNotExist:
            ct = CourseTeacher.objects.create(course=course, teacher=user)

        name = user.get_full_name()
        if not name:
            name = user.username
        data = {
            'id': ct.id,
            'order': ct.order,
            'name': name,
            'gravatar': gravatar_img_for_email(user.email, 20),
            'pending': False
        }
        response = HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')
    elif response is None:
        if Invitation.objects.filter(email=email_or_id, course=course).count() == 0:
            invitation = Invitation(host=request.user, email=email_or_id,
                                    course=course, datetime=datetime.now())
            invitation.save()
            send_invitation(request, invitation)
            data = {
                'name': email_or_id,
                'gravatar': gravatar_img_for_email(email_or_id, 20),
                'pending': True
            }
            response = HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')
        else:
            response = HttpResponse(status=409)

    return response


@is_teacher_or_staff
def teacheradmin_teachers_transfer(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    ident = request.POST['data']

    if request.user != course.owner:
        return HttpResponse(status=401)

    response = HttpResponse()

    try:
        user = CourseTeacher.objects.get(id=ident).teacher
        course.owner = user
        course.save()
    except (ValueError, CourseTeacher.DoesNotExist):
        response = HttpResponse(status=404)

    return response


@is_teacher_or_staff
def teacheradmin_teachers_reorder(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    try:
        new_order = simplejson.loads(request.raw_post_data)
    except ValueError:
        return HttpResponse(status=400)

    response = HttpResponse()

    cts_map = dict([(cts.id, cts)
                    for cts in CourseTeacher.objects.filter(course=course)])

    for i, course_teacher_id in enumerate(new_order):
        cid = int(course_teacher_id)
        ct = cts_map.get(cid, None)
        if ct is None:
            return HttpResponse(status=404)
        else:
            ct.order = i
            ct.save()

    return response


@is_teacher_or_staff
def teacheradmin_info(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    external_apps = externalapps.all()

    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        static_page_form = StaticPageForm(data=request.POST, instance=course.static_page)
        if form.is_valid() and static_page_form.is_valid():
            static_page = static_page_form.save(commit=False)
            static_page.save()
            course = form.save(commit=False)
            course.static_page = static_page
            course.save()

            messages.success(request, _(u"Your changes were saved."))

            return HttpResponseRedirect(reverse('teacheradmin_info',
                                                args=[course_slug]))
        else:
            messages.error(request, _(u"There were problems with some data you introduced, please fix them and try again."))
    else:
        form = CourseForm(instance=course)
        static_page_form = StaticPageForm(instance=course.static_page)

    return render_to_response('teacheradmin/info.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'form': form,
        'static_page_form': static_page_form,
        'external_apps': external_apps,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_categories(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        category_list = []
        for key in request.POST.keys():
            if key.startswith('cat-'):
                slug = key[4:]
                try:
                    category = Category.objects.get(slug=slug,
                                                    only_admins=False)
                    category_list.append(category)
                except Category.DoesNotExist:
                    messages.error(request, _(u'There were problems with some data you introduced, please fix them and try again.'))
                    return HttpResponseRedirect(
                        reverse('teacheradmin_categories', args=[course_slug]))
        admin_cats = course.categories.filter(only_admins=True)
        category_list.extend(admin_cats)
        course.categories.clear()
        course.categories.add(*category_list)
        course.save()
        messages.success(request, _(u"Your changes were saved."))
        return HttpResponseRedirect(reverse('teacheradmin_categories',
                                            args=[course_slug]))

    counter = 0
    categories = []
    aux = []
    for cat in Category.objects.filter(only_admins=False):
        counter += 1
        aux.append({
            'cat': cat,
            'checked': cat in course.categories.all(),
        })
        if counter % 5 == 0:
            categories.append(aux)
            aux = []
    if len(aux) < 5 and len(aux) > 0:
        categories.append(aux)

    return render_to_response('teacheradmin/categories.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'categories': categories,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_assets(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    assets = course_get_assets(course).order_by('id').distinct()

    return render_to_response('teacheradmin/assets.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'assets': assets,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_assets_edit(request, course_slug, asset_id):

    asset = get_object_or_404(Asset, id=asset_id)
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = AssetTeacherForm(request.POST, instance=asset)
        if form.is_valid():

            form_name = form.cleaned_data['name']
            form_capacity = form.cleaned_data['capacity']
            form_description = form.cleaned_data['description']

            if asset is not None:

                asset.name = form_name
                asset.capacity = form_capacity
                asset.description = form_description

            asset.save()

            return HttpResponseRedirect(
                reverse("teacheradmin_assets",
                        args=[course_slug]))

    else:
        form = AssetTeacherForm(instance=asset)

    return render_to_response('teacheradmin/asset_edit.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'form': form,
        'asset': asset,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    announcements = course.announcement_set.all()

    return render_to_response('teacheradmin/announcements.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcements': announcements,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_view(request, course_slug, announ_id, announ_slug):
    announcement = get_object_or_404(Announcement, id=announ_id)
    course = announcement.course
    is_enrolled = course.students.filter(id=request.user.id).exists()
    return render_to_response('teacheradmin/announcement_view.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcement': announcement,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_add_or_edit(request, course_slug, announ_id=None, announ_slug=None):

    if announ_id is None:
        announcement = None
        course = get_object_or_404(Course, slug=course_slug)
    else:
        announcement = get_object_or_404(Announcement, id=announ_id)
        course = announcement.course

    is_enrolled = course.students.filter(id=request.user.id).exists()
    students = course.students.count()
    data = None
    if request.method == 'POST':
        data = request.POST
    massive_emails = course.massive_emails.all()
    form = AnnouncementForm(data=data, instance=announcement, course=course)
    remain_send_emails = form.remain_send_emails(massive_emails)
    if form.is_valid():
        announcement = form.save()
        messages.success(request,
                         _("The announcement was created successfully."))
        if form.cleaned_data.get('send_email', None):
            messages.success(
                request,
                _("The email has been queued, and it will be send in batches to every student in the course.")
            )

        return HttpResponseRedirect(
            reverse("teacheradmin_announcements_view",
                    args=[course_slug, announcement.id, announcement.slug]))

    return render_to_response('teacheradmin/announcement_edit.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'form': form,
        'announcement': announcement,
        'remain_send_emails': remain_send_emails,
        'students': students
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_delete(request, course_slug, announ_id, announ_slug):

    announcement = get_object_or_404(Announcement, id=announ_id)
    announcement.delete()

    return HttpResponseRedirect(reverse("teacheradmin_announcements", args=[course_slug]))


@is_teacher_or_staff
def teacheradmin_emails(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    students = course.students.count()
    data = None
    if request.method == 'POST':
        data = request.POST
    massive_emails = course.massive_emails.all()
    form = MassiveEmailForm(data=data, course=course)
    remain_send_emails = form.remain_send_emails(massive_emails)
    if remain_send_emails > 0 and form.is_valid():
        form.save()
        messages.success(request, _("The email has been queued, and it will be send in batches to every student in the course."))
        return HttpResponseRedirect(reverse('teacheradmin_stats', args=[course_slug]))
    return render_to_response('teacheradmin/emails.html', {
        'course': course,
        'massive_emails': massive_emails,
        'remain_send_emails': remain_send_emails,
        'is_enrolled': is_enrolled,
        'students': students,
        'form': form,
    }, context_instance=RequestContext(request))
