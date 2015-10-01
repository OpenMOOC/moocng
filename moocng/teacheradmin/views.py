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

from django.conf import settings

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
from django.db.models import Q

from moocng.courses.models import (Course, CourseTeacher, CourseStudent, KnowledgeQuantum,
                                   Option, Announcement, Unit, Attachment, Language,
                                   Transcription, get_transcription_types_choices)
from moocng.courses.utils import UNIT_BADGE_CLASSES, get_course_students_csv, get_course_teachers_csv, get_csv_from_students_list
from moocng.courses.marks import calculate_course_mark, get_units_info_from_course, get_kqs_info_from_unit
from moocng.courses.security import get_tasks_published
from moocng.categories.models import Category
from moocng.profile.models import UserProfile
from moocng.media_contents import get_media_content_types_choices
from moocng.mongodb import get_db
from moocng.portal.templatetags.gravatar import gravatar_img_for_email
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.forms import (CourseForm, AnnouncementForm,
                                       MassiveEmailForm, AssetTeacherForm,
                                       StaticPageForm, GroupsForm)
from moocng.teacheradmin.models import Invitation, MassiveEmail
from moocng.teacheradmin.tasks import send_massive_email_task
from moocng.teacheradmin.utils import (send_invitation_registered,
                                       send_removed_notification,
                                       send_invitation_not_registered,
                                       get_num_students_passed_course,
                                       get_num_students_completed_course,
                                       get_num_students_started_course,
                                       get_num_students_passed_unit,
                                       get_num_students_completed_unit,
                                       get_num_students_started_unit)
from moocng.videos.tasks import process_video_task

from moocng.assets.utils import course_get_assets
from moocng.assets.models import Asset
from moocng.externalapps.models import externalapps

from moocng.badges.models import BadgeByCourse

import pprint

from django.core import serializers
from dateutil.relativedelta import relativedelta

import boto

@is_teacher_or_staff
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    stats_course = get_db().get_collection('stats_course')
    stats = stats_course.find_one({'course_id': course.id})

    if stats is not None:
        num_kqs = 0
        for unit in course.unit_set.filter(Q(status='p') | Q(status='o') | Q(status='l')).all():
            num_kqs += unit.knowledgequantum_set.count()

        enrolled = course.students.count()
        started = get_num_students_started_course(course)
        if started > enrolled:
            enrolled = started

        data = {
            'enrolled': enrolled,
            'started': started,
            'completed': get_num_students_completed_course(course),
            'num_units': course.unit_set.filter(Q(status='p') | Q(status='o') | Q(status='l')).count(),
            'num_kqs': num_kqs,
            'num_tasks': len(get_tasks_published(course))
        }

        if course.threshold is not None:
            #if the course doesn't support certification, then don't return the
            #'passed' stat since it doesn't apply
            passed = get_num_students_passed_course(course)
            data['passed'] = passed

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
def teacheradmin_stats_students(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    enrolled = course.students.count()
    started = get_num_students_started_course(course)
    if started > enrolled:
        enrolled = started
    data = {
        "enrolled": enrolled,
        "byCountry": {},
        "byLanguage": {},
        "byGender": {},
        "byAge": {
            "0-10": 0,
            "11-20": 0,
            "21-30": 0,
            "31-40": 0,
            "41-50": 0,
            "51-60": 0,
            "61-70": 0,
            "71-80": 0,
            "81-90": 0,
            "91-100": 0,
            "+100": 0,
        },
        "byLocations": []
    }

    stats_course = get_db().get_collection("stats_course")
    stats = stats_course.find_one({"course_id": course.id})

    if stats is not None:
        data["started"] = started
        data["completed"] = get_num_students_completed_course(course)

        if course.threshold is not None:
            passed = get_num_students_passed_course(course)
            data["passed"] = passed

    data["byGender"]["male"] = CourseStudent.objects.filter(course=course,student__userprofile__gender='male').count()
    data["byGender"]["female"] = CourseStudent.objects.filter(course=course,student__userprofile__gender='female').count()
    data["byGender"]["unknown"] = data["enrolled"] - data["byGender"]["male"] - data["byGender"]["female"]

    total_language = 0
    for lang in settings.LANGUAGES:
        data["byLanguage"][lang[0]] = CourseStudent.objects.filter(course=course,student__userprofile__language=lang[0]).count()
        total_language += data["byLanguage"][lang[0]]
    data["byLanguage"]["unknown"] = data["enrolled"] - total_language

    total_country = 0
    for elem in UserProfile.objects.all().distinct("country"):
        if elem.country:
            data["byCountry"][elem.country] = CourseStudent.objects.filter(course=course,student__userprofile__country=elem.country).count()
            total_country += data["byCountry"][elem.country]
    data["byCountry"]["unknown"] = data["enrolled"] - total_country

    now = datetime.now()
    total_unknown_age = 0
    for student in CourseStudent.objects.filter(course=course):
        if student.student.get_profile().birthdate:
            years = relativedelta(now, student.student.get_profile().birthdate).years
            if years >= 0 and years <= 10:
                data["byAge"]["0-10"] += 1
            elif years > 10 and years <= 20:
                data["byAge"]["11-20"] += 1
            elif years > 20 and years <= 30:
                data["byAge"]["21-30"] += 1
            elif years > 30 and years <= 40:
                data["byAge"]["31-40"] += 1
            elif years > 40 and years <= 50:
                data["byAge"]["41-50"] += 1
            elif years > 50 and years <= 60:
                data["byAge"]["51-60"] += 1
            elif years > 60 and years <= 70:
                data["byAge"]["61-70"] += 1
            elif years > 70 and years <= 80:
                data["byAge"]["71-80"] += 1
            elif years > 80 and years <= 90:
                data["byAge"]["81-90"] += 1
            elif years > 90 and years <= 100:
                data["byAge"]["91-100"] += 1
            elif years > 100:
                data["byAge"]["+100"] += 1
        else:
            total_unknown_age += 1
        if student.pos_lat:
            data["byLocations"].append({"lon": student.pos_lon, "lat": student.pos_lat})

    if total_unknown_age > 0:
        data["byAge"]["unknown"] = total_unknown_age

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@is_teacher_or_staff
def teacheradmin_stats_teachers(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    data = {
        "total": course.teachers.count(),
        "byCountry": {},
        "byLanguage": {},
        "byGender": {},
        "byAge": {
            "0-10": 0,
            "11-20": 0,
            "21-30": 0,
            "31-40": 0,
            "41-50": 0,
            "51-60": 0,
            "61-70": 0,
            "71-80": 0,
            "81-90": 0,
            "91-100": 0,
            "+100": 0,
        },
        "byOrganization": {}
    }

    data["byGender"]["male"] = CourseTeacher.objects.filter(course=course,teacher__userprofile__gender='male').count()
    data["byGender"]["female"] = CourseTeacher.objects.filter(course=course,teacher__userprofile__gender='female').count()
    data["byGender"]["unknown"] = data["total"] - data["byGender"]["male"] - data["byGender"]["female"]

    total_language = 0
    for lang in settings.LANGUAGES:
        data["byLanguage"][lang[0]] = CourseTeacher.objects.filter(course=course,teacher__userprofile__language=lang[0]).count()
        total_language += data["byLanguage"][lang[0]]
    data["byLanguage"]["unknown"] = data["total"] - total_language

    total_country = 0
    for elem in UserProfile.objects.all().distinct("country"):
        if elem.country:
            data["byCountry"][elem.country] = CourseTeacher.objects.filter(course=course,teacher__userprofile__country=elem.country).count()
            total_country += data["byCountry"][elem.country]
    data["byCountry"]["unknown"] = data["total"] - total_country

    now = datetime.now()
    total_unknown_age = 0
    for teacher in CourseTeacher.objects.filter(course=course):
        if teacher.teacher.get_profile().birthdate:
            years = relativedelta(now, teacher.teacher.get_profile().birthdate).years
            if years >= 0 and years <= 10:
                data["byAge"]["0-10"] += 1
            elif years > 10 and years <= 20:
                data["byAge"]["11-20"] += 1
            elif years > 20 and years <= 30:
                data["byAge"]["21-30"] += 1
            elif years > 30 and years <= 40:
                data["byAge"]["31-40"] += 1
            elif years > 40 and years <= 50:
                data["byAge"]["41-50"] += 1
            elif years > 50 and years <= 60:
                data["byAge"]["51-60"] += 1
            elif years > 60 and years <= 70:
                data["byAge"]["61-70"] += 1
            elif years > 70 and years <= 80:
                data["byAge"]["71-80"] += 1
            elif years > 80 and years <= 90:
                data["byAge"]["81-90"] += 1
            elif years > 90 and years <= 100:
                data["byAge"]["91-100"] += 1
            elif years > 100:
                data["byAge"]["+100"] += 1
        else:
            total_unknown_age += 1

        organizations = teacher.teacher.get_profile().organization.all()
        total_unknown_org = 0
        if len(organizations):
            for v in organizations:
                if v.name not in data["byOrganization"]:
                    data["byOrganization"][v.name] = 1
                else:
                    data["byOrganization"][v.name] += 1
        else:
            total_unknown_org += 1

    if total_unknown_age > 0:
        data["byAge"]["unknown"] = total_unknown_age
    if total_unknown_org > 0:
        data["byOrganization"]["unknown"] = total_unknown_org

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@is_teacher_or_staff
def teacheradmin_stats_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    stats_unit = get_db().get_collection('stats_unit')
    data = []
    units = Unit.objects.filter((Q(status='p') | Q(status='o') | Q(status='l')) & Q(course__id=course.id))
    for unit in units:
        stats = stats_unit.find_one({'unit_id': unit.id})

        if stats is not None:
            unit_data = {
                'id': unit.id,
                'title': unit.title,
                'started': get_num_students_started_unit(unit),
                'completed': get_num_students_completed_unit(unit),
            }

            if course.threshold is not None:
                # if the course doesn't support certification, then don't return
                # the 'passed' stat since it doesn't apply
                passed = get_num_students_passed_unit(unit)
                unit_data['passed'] = passed

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
                passed = get_num_students_passed_course(course)
                kq_data['passed'] = passed

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
        'transcription_type_choices': get_transcription_types_choices(),
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
def teacheradmin_units_transcription(request, course_slug):
    if request.method == 'POST':
        if not 'kq' in request.GET:
            return HttpResponse(status=400)
        kq = get_object_or_404(KnowledgeQuantum, id=request.GET['kq'])

        if not('transcription' in request.FILES.keys()):
            return HttpResponse(status=400)

        uploaded_file = request.FILES['transcription']
        language = Language.objects.get(id=request.POST['language'])
        transcription_type = request.POST['type']
        transcription = Transcription(filename=uploaded_file, kq=kq, transcription_type=transcription_type, language=language)
        transcription.save()

        return HttpResponse()

    elif request.method == 'DELETE':
        if not 'transcription' in request.GET:
            return HttpResponse(status=400)

        transcription = get_object_or_404(Transcription,
                                       id=request.GET['transcription'])
        transcription.delete()

        return HttpResponse()

    else:
        return HttpResponse(status=400)

@is_teacher_or_staff
def teacheradmin_units_s3upload(request, course_slug):
    if request.method == 'POST':
        if not 'kq' in request.GET:
            return HttpResponse(status=400)
        kq = get_object_or_404(KnowledgeQuantum, id=request.GET['kq'])

        if not('file' in request.FILES.keys()):
            return HttpResponse(status=400)

        file_to_upload = request.FILES.get('file', None)

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = boto.s3.key.Key(bucket)
        name = "files/%s/%s" % (kq.id, file_to_upload.name)
        k.key = name
        k.set_contents_from_file(file_to_upload)
        k.make_public()
        url = k.generate_url(expires_in=0, query_auth=False)
        print "Url for updated file: %s" % (url)
        #Save multimedia_content_id and multimedia_content_type?

        return HttpResponse(simplejson.dumps({'url': url}), mimetype="application/json")

    elif request.method == 'DELETE':
        if not 'transcription' in request.GET:
            return HttpResponse(status=400)

        transcription = get_object_or_404(Transcription,
                                       id=request.GET['transcription'])
        transcription.delete()

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
        goback = reverse('teacheradmin_units', args=(course.slug,)) + '#kq' + kq_id
        # goback = request.META['HTTP_REFERER']
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
                'order': opt.order, 'name': opt.name
                } for opt in obj.option_set.all()]
        context = {
            'course': course,
            'kq': kq,
            'is_enrolled': is_enrolled,
            'object_id': obj.id,
            'original': obj,
            'options_json': simplejson.dumps(json, sort_keys=True),
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
        send_invitation_registered(request, user.email, course)
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
            send_invitation_not_registered(request, invitation)
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
            form.save_m2m()

            messages.success(request, _(u"Your changes were saved."))

            return HttpResponseRedirect(reverse('teacheradmin_info',
                                                args=[course_slug]))
        else:
            print form.errors
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
        'thumb_rec_height': course.THUMBNAIL_HEIGHT,
        'thumb_rec_width': course.THUMBNAIL_WIDTH,
        'back_rec_height': course.BACKGROUND_HEIGHT,
        'back_rec_width': course.BACKGROUND_WIDTH,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_groups(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = GroupsForm(data=request.POST, instance=course)
        if form.is_valid():
            course = form.save()

            messages.success(request, _(u"Your changes were saved."))

            return HttpResponseRedirect(reverse('teacheradmin_groups',
                                                args=[course_slug]))
    else:
        form = GroupsForm(instance=course)

        if(get_db().get_collection('groups').find({"id_course":course.id}).count() > 0):
            disabled = None
        else:
            disabled =True

    return render_to_response('teacheradmin/groups.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'disabled': disabled,
        'form': form,
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
def teacheradmin_badges(request, course_slug, badge_id=None):

    course = get_object_or_404(Course, slug=course_slug)

    if request.method == 'POST':
        try:
            badge_id = int(request.POST["badgeId"])
        except:
            badge_id = None
        badge_title = request.POST['badgeTitle']
        badge_description = request.POST["badgeDescription"]
        badge_note = request.POST['noteBadge']
        badge_color = request.POST['colorBadge']
        criteria_type = int(request.POST["criteriaType"])
        if(criteria_type != 1):
            criteria = request.POST["unitBadge"]
        else:
            criteria = ','.join(request.POST.getlist('pillsBadge'))

        if not badge_id:
            badge = BadgeByCourse.create(badge_title, badge_description, criteria, criteria_type, badge_note, badge_color, course)
        else:
            badge = BadgeByCourse.objects.get(id=badge_id)
            badge.title = badge_title
            badge.description = badge_description
            badge.note = badge_note
            badge.color = badge_color
            badge.criteria_type = criteria_type
            badge.criteria = criteria

        badge.save()

        return HttpResponseRedirect("/course/" + course_slug + "/teacheradmin/badges/")




    units = course.unit_set.all().order_by('order')

    knowledgequantum = []
    pills = []
    if(units and len(units) > 0):
        pills = units[0].knowledgequantum_set.filter(peerreviewassignment__isnull=False).order_by("order")

    badge = None
    if badge_id:
        badge = BadgeByCourse.objects.get(id=badge_id)
        if badge.criteria_type == 1:
            try:
                criteria_list = [int(n) for n in badge.criteria.split(',')]
                criteria_items = KnowledgeQuantum.objects.filter(id__in=criteria_list)
                badge.criteria = criteria_items
            except:
                pass


    return render_to_response('teacheradmin/badges.html', {
        'course': course,
        'units': units,
        'pills':pills,
        'badges':BadgeByCourse.objects.filter(course_id = course.id).order_by("title"),
        'badge': badge,
    }, context_instance=RequestContext(request))

@is_teacher_or_staff
def reload_pills(request,course_slug,id):

    result = {"result":[]};
    pills = KnowledgeQuantum.objects.filter(unit_id = id).filter(peerreviewassignment__isnull=False).order_by("order")
    for pill in pills:
        result["result"].append({"id":pill.id, "title":pill.title})

    return HttpResponse(simplejson.dumps(result), content_type="application/json")


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
def delete_badge(request, course_slug, id):
    BadgeByCourse.objects.filter(id=id).delete()
    return HttpResponse("true")


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

@is_teacher_or_staff
def teacheradmin_lists(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/lists.html', {
        'course': course,
        'is_enrolled': is_enrolled
    }, context_instance=RequestContext(request))

def _get_students_completed_kqs_filter(course):
    activity_col = get_db().get_collection('activity')
    pipeline = [
        {'$match': {'course_id': course.pk} },
        {'$group': {'_id': '$user_id', 'kqs': {'$sum': 1} } }
    ]
    student_list = activity_col.aggregate(pipeline)
    return student_list['result']

def _get_students_by_filter(filter, course):
    marks_course_col = get_db().get_collection('marks_course')
    num_kqs = 0
    for unit in course.unit_set.filter(Q(status='p') | Q(status='o') | Q(status='l')).all():
        num_kqs += unit.knowledgequantum_set.count()

    students = []
    if filter == 'started':
        students = CourseStudent.objects.filter(course=course, student__pk__in=[int(d['_id']) for d in _get_students_completed_kqs_filter(course)]),
    elif filter == 'notstarted':
        students = CourseStudent.objects.filter(course=course).exclude(student__pk__in=[int(d['_id']) for d in _get_students_completed_kqs_filter(course)]),
    elif filter == 'completed':
        students = CourseStudent.objects.filter(course=course, student__pk__in=[int(d['_id']) for d in _get_students_completed_kqs_filter(course) if d['kqs'] >= num_kqs]),
    elif filter == 'notcompleted':
        students = CourseStudent.objects.filter(course=course).exclude(student__pk__in=[int(d['_id']) for d in _get_students_completed_kqs_filter(course) if d['kqs'] >= num_kqs]),
    elif filter == 'passed':
        students = CourseStudent.objects.filter(course=course, student__pk__in=[int(d['user_id']) for d in list(marks_course_col.find({'course_id': course.pk, 'mark': {'$gte': float(course.threshold)} }))]),
    elif filter == 'notpassed':
        students = CourseStudent.objects.filter(course=course).exclude(student__pk__in=[int(d['user_id']) for d in list(marks_course_col.find({'course_id': course.pk, 'mark': {'$gte': float(course.threshold)} }))])

    try:
        if isinstance(students, tuple):
            return students[0]
        else:
            return students
    except:
        return []

@is_teacher_or_staff
def teacheradmin_lists_coursestudents(request, course_slug, format=None, filter=None):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    accumulative_students = get_num_students_started_course(course)
    students = course.students.all()
    if students.count() > accumulative_students:
        accumulative_students = students.count()

    if not filter:
        students = course.students.all()
    else:
        students = _get_students_by_filter(filter, course)

    if format is None:
        headers = [_(u"First name"), _(u"Last name"), _(u"Email"), _(u"Date joined"), _(u"Last login"), _(u"View details")]
        elements = []

        if len(students):
            if not hasattr(students[:1][0], 'student'):
                for student in students:
                    try:
                        element = [student.first_name, student.last_name, student.email, student.date_joined.strftime('%d/%m/%Y'), student.last_login.strftime('%d/%m/%Y'), {"caption": _(u"Go"), "link": reverse('teacheradmin_lists_coursestudents_detail', args=[course.slug, student.username])}]
                        elements.append(element)
                    except:
                        continue
            else:
                for student in students:
                    try:
                        element = [student.student.first_name, student.student.last_name, student.student.email, student.student.date_joined.strftime('%d/%m/%Y'), student.student.last_login.strftime('%d/%m/%Y'), {"caption": _(u"Go"), "link": reverse('teacheradmin_lists_coursestudents_detail', args=[course.slug, student.student.username])}]
                        elements.append(element)
                    except:
                        continue
        return render_to_response('teacheradmin/list_table.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'headers': headers,
            'elements': elements,
            'accumulative_students': accumulative_students
        }, context_instance=RequestContext(request))

    elif format == 'csv':
        students_list = get_course_students_csv(course)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (course_slug)
        response.write(students_list)
        return response

@is_teacher_or_staff
def teacheradmin_lists_coursestudentsmarks(request, course_slug, format=None, filter=None):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    accumulative_students = get_num_students_started_course(course)
    students = course.students.all()
    if students.count() > accumulative_students:
        accumulative_students = students.count()

    if not filter:
        students = course.students.all()
    else:
        students = list(_get_students_by_filter(filter, course))

    if format is None:
        headers = [_(u"First name"), _(u"Last name"), _(u"Email"), _(u"Course mark"), _(u"View details")]
        elements = []

        if len(students):
            if not hasattr(students[:1][0], 'student'):
                for student in students:
                    try:
                        mark, mark_info = calculate_course_mark(course, student)
                        element = [student.first_name, student.last_name, student.email, "%.2f" % mark, {"caption": _(u"Go"), "link": reverse('teacheradmin_lists_coursestudents_detail', args=[course.slug, student.username])}]
                        elements.append(element)
                    except:
                        continue
            else:
                for student in students:
                    try:
                        mark, mark_info = calculate_course_mark(course, student.student)
                        element = [student.student.first_name, student.student.last_name, student.student.email, "%.2f" % mark, {"caption": _(u"Go"), "link": reverse('teacheradmin_lists_coursestudents_detail', args=[course.slug, student.student.username])}]
                        elements.append(element)
                    except:
                        continue
        return render_to_response('teacheradmin/list_table.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'headers': headers,
            'elements': elements,
            'accumulative_students': accumulative_students,
        }, context_instance=RequestContext(request))

    elif format == 'csv':
        students_list = get_csv_from_students_list(course, students)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (course_slug)
        response.write(students_list)
        return response

@is_teacher_or_staff
def teacheradmin_lists_coursestudents_detail(request, course_slug, username, format=None):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    student = get_object_or_404(User, username=username)
    mark, mark_info = calculate_course_mark(course, student)
    units = get_units_info_from_course(course, student)
    headers = [_(u"Title"), _(u"Mark"), _(u"Relative mark")]
    elements = []
    for unitmark in units:
        try:
            unit = Unit.objects.get(pk=unitmark["unit_id"])
            element = {"title": unit.title, "mark": "%.2f" % unitmark["mark"], "relative_mark": "%.2f" % unitmark["relative_mark"], "order": unit.order}
            element["kqs"] = []
            kqs = get_kqs_info_from_unit(unit, student)
            for kqmark in kqs:
                try:
                    kq = KnowledgeQuantum.objects.get(pk=kqmark["kq_id"])
                    element_kq = {"title": kq.title, "mark": "%.2f" % kqmark["mark"], "relative_mark": "%.2f" % kqmark["relative_mark"], "order": kq.order}
                    element["kqs"].append(element_kq)
                except:
                    pass
            element["kqs"].sort(key=lambda x: x["order"], reverse=False)

            elements.append(element)
        except:
            pass
    elements.sort(key=lambda x: x["order"], reverse=False)

    return render_to_response('teacheradmin/lists_student_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'student': student,
        'course_mark': "%.2f" % mark,
        'headers': headers,
        'elements': elements,
    }, context_instance=RequestContext(request))

@is_teacher_or_staff
def teacheradmin_lists_courseteachers(request, course_slug, format=None):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if format is None:
        headers = [_(u"First name"), _(u"Last name"), _(u"Email"), _(u"Organization"), _(u"Date joined"), _(u"Last login"), _(u"View details")]
        elements = []

        teachers_ids = set(teacher.id for teacher in course.teachers.all())
        for student in course.students.filter(pk__in=teachers_ids):
            organizations = student.get_profile().organization.all()
            organization = organizations[0].name if len(organizations) > 0 else ""
            element = [student.first_name, student.last_name, student.email, organization, student.date_joined.strftime('%d/%m/%Y'), student.last_login.strftime('%d/%m/%Y'), {"caption": _(u"Go"), "link": reverse('teacheradmin_lists_coursestudents_detail', args=[course.slug, student.username])}]
            elements.append(element)
        return render_to_response('teacheradmin/list_table.html', {
            'course': course,
            'is_enrolled': is_enrolled,
            'headers': headers,
            'elements': elements,
        }, context_instance=RequestContext(request))

    elif format == 'csv':
        students_list = get_course_teachers_csv(course)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (course_slug)
        response.write(students_list)
        return response
