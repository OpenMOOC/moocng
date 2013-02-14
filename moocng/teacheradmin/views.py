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

from gravatar.templatetags.gravatar import gravatar_img_for_email

from moocng.api.mongodb import get_db
from moocng.courses.models import (Course, CourseTeacher, KnowledgeQuantum,
                                   Option, Announcement, Unit)
from moocng.courses.forms import AnnouncementForm
from moocng.courses.utils import (UNIT_BADGE_CLASSES, calculate_course_mark,
                                  calculate_unit_mark, calculate_kq_mark)
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.forms import CourseForm, MassiveEmailForm
from moocng.teacheradmin.models import Invitation
from moocng.teacheradmin.tasks import send_massive_email_task
from moocng.teacheradmin.utils import (send_invitation,
                                       send_removed_notification)
from moocng.videos.tasks import process_video_task


@is_teacher_or_staff
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    activity = get_db().get_collection('activity')

    data = {
        'enrolled': course.students.count(),
        'started': 0,
        'completed': 0
    }

    if course.threshold is not None:
        # if the course doesn't support certification, then don't return the
        # 'passed' stat since it doesn't apply
        data['passed'] = 0
        for student in course.students.all():
            if calculate_course_mark(course, student)[0] >= float(course.threshold):
                data['passed'] += 1

    units = course.unit_set.all()
    kqs = 0
    for unit in units:
        kqs += unit.knowledgequantum_set.count()

    for student in course.students.all():
        user_activity_list = activity.find_one({'user': student.id}, safe=True)

        if user_activity_list is not None:
            visited_kqs = user_activity_list.get('courses', {}).get(unicode(course.id), {}).get('kqs', [])

            if len(visited_kqs) > 0:
                data['started'] += 1
            if len(visited_kqs) == kqs:
                data['completed'] += 1

    return render_to_response('teacheradmin/stats.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'initial_data': simplejson.dumps(data),
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_stats_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    data = []
    use_old_calculus = False
    if course.slug in settings.COURSES_USING_OLD_TRANSCRIPT:
        use_old_calculus = True
    activity = get_db().get_collection('activity')

    unit_list = course.unit_set.all()
    for unit in unit_list:
        unit_data = {
            'id': unit.id,
            'title': unit.title,
            'started': 0,
            'completed': 0
        }

        if course.threshold is not None:
            # if the course doesn't support certification, then don't return
            # the 'passed' stat since it doesn't apply
            unit_data['passed'] = 0
            for student in course.students.all():
                if calculate_unit_mark(unit, student, use_old_calculus)[0] >= float(course.threshold):
                    unit_data['passed'] += 1

        kqs = [kq.id for kq in unit.knowledgequantum_set.all()]
        for student in course.students.all():
            user_activity_list = activity.find_one({'user': student.id}, safe=True)

            if user_activity_list is not None:
                visited_kqs = user_activity_list.get('courses', {}).get(unicode(course.id), {}).get('kqs', [])

                started = 0
                completed = 0
                for kq in visited_kqs:
                    if int(kq) in kqs:
                        started = 1
                        completed += 1

                unit_data['started'] += started
                if len(kqs) == completed:
                    unit_data['completed'] += 1

        data.append(unit_data)

    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_stats_kqs(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not 'unit' in request.GET:
        return HttpResponse(status=400)
    unit = get_object_or_404(Unit, id=request.GET['unit'])
    if not unit in course.unit_set.all():
        return HttpResponse(status=400)
    data = []
    activity = get_db().get_collection('activity')
    answers = get_db().get_collection('answers')

    kq_list = unit.knowledgequantum_set.all()
    for kq in kq_list:
        kq_data = {
            'id': kq.id,
            'title': kq.title,
            'viewed': 0
        }

        question = None
        if kq.question_set.count() > 0:
            question = kq.question_set.all()[0]
            kq_data['answered'] = 0

            if course.threshold is not None:
                # if the course doesn't support certification, then don't
                # return the 'passed' stat since it doesn't apply
                kq_data['passed'] = 0
                for student in course.students.all():
                    if calculate_kq_mark(kq, student) >= float(course.threshold):
                        kq_data['passed'] += 1

        for student in course.students.all():
            user_activity_list = activity.find_one({'user': student.id}, safe=True)

            if user_activity_list is not None:
                visited_kqs = user_activity_list.get('courses', {}).get(unicode(course.id), {}).get('kqs', [])
                visited_kqs = [int(vkq) for vkq in visited_kqs]

                if kq.id in visited_kqs:
                    kq_data['viewed'] += 1

            if question is not None:
                user_answer_list = answers.find_one({'user': student.id}, safe=True)
                if user_answer_list is not None:
                    answer = user_answer_list.get('questions', {}).get(unicode(question.id))
                    if answer:
                        kq_data['answered'] += 1

        data.append(kq_data)

    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/units.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'unit_badge_classes': simplejson.dumps(UNIT_BADGE_CLASSES),
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
        user = User.objects.get(id=ident)
        course.owner = user
        course.save()
    except (ValueError, User.DoesNotExist):
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

    if request.method == 'POST':
        form = CourseForm(data=request.POST, files=request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, _(u"Your changes were saved."))

            return HttpResponseRedirect(reverse('teacheradmin_info',
                                                args=[course_slug]))
        else:
            messages.error(request, _(u"There were problems with some data you introduced, please fix them and try again."))
    else:
        form = CourseForm(instance=course)

    return render_to_response('teacheradmin/info.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'form': form,
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
def teacheradmin_announcements_view(request, course_slug, announ_slug):
    announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)
    course = announcement.course
    is_enrolled = course.students.filter(id=request.user.id).exists()
    return render_to_response('teacheradmin/announcement_view.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcement': announcement,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_edit(request, course_slug, announ_slug=None):

    if announ_slug is None:
        announcement = None
    else:
        announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)

    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.instance.slug = slugify(form.instance.title)
            if Announcement.objects.filter(slug=form.instance.slug).exists():
                messages.error(request, _("There is a announce with the same title"))
            else:
                if not announcement:
                    form.instance.course = course
                form.save()

                return HttpResponseRedirect(reverse("teacheradmin_announcements_view", args=[course_slug, form.instance.slug]))

    else:
        form = AnnouncementForm(instance=announcement)

    return render_to_response('teacheradmin/announcement_edit.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcement': announcement,
        'form': form,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_delete(request, course_slug, announ_slug):

    announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)
    announcement.delete()

    return HttpResponseRedirect(reverse("teacheradmin_announcements", args=[course_slug]))


@is_teacher_or_staff
def teacheradmin_emails(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    students = course.students.count()

    if request.method == 'POST':
        form = MassiveEmailForm(request.POST)
        if form.is_valid():
            form.instance.course = course
            form.instance.datetime = datetime.now()
            form.save()

            batch = 30
            try:
                batch = settings.MASSIVE_EMAIL_BATCH_SIZE
            except AttributeError:
                pass

            batches = (course.students.count() / batch) + 1
            students = course.students.all()
            for i in range(batches):
                init = batch * i
                end = init + batch
                students_ids = [s.id for s in students[init:end]]
                send_massive_email_task.delay(form.instance.id, students_ids)

            messages.success(request, _("The email has been queued, and it will be send in batches to every student in the course."))
            return HttpResponseRedirect(reverse('teacheradmin_stats', args=[course_slug]))
    else:
        form = MassiveEmailForm()

    return render_to_response('teacheradmin/emails.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'students': students,
        'form': form,
    }, context_instance=RequestContext(request))
