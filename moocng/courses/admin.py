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

import logging

from functools import update_wrapper


from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.contrib import messages
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from celery.task.control import inspect

from adminsortable.admin import SortableAdmin

from moocng.admin import MassiveGlobalAdmin
from moocng.courses.forms import UnitForm, AttachmentForm
from moocng.courses.models import (Course, Announcement, Unit, KnowledgeQuantum,
                                   StaticPage)
from moocng.courses.models import Question, Option, Attachment, Language
from moocng.courses.models import CourseTeacher,CourseLanguage
from moocng.courses.utils import clone_course
from moocng.courses.widgets import ImageReadOnlyWidget
from moocng.teacheradmin.forms import MassiveGlobalAnnouncementAdminForm
from moocng.videos.tasks import process_video_task


logger = logging.getLogger(__name__)


class CourseAdmin(SortableAdmin):

    """
    Administration panel for the Course. This inherits from SortableAdmin, which
    allows to sort the list of courses as desired.

    .. versionadded:: 0.1
    """

    prepopulated_fields = {'slug': ('name', )}
    exclude = ('students', 'teachers')
    raw_id_fields = ('owner',)
    autocomplete_lookup_fields = {'fk': ['owner'], }
    search_fields = ('name', 'slug')

    def get_urls(self):
        urlpatterns = super(CourseAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^(.+)/clone/$',
                wrap(self.clone_course),
                name='clone_course'),
        ) + urlpatterns
        return urlpatterns

    def clone_course(self, request, object_id, form_url='', extra_context=None, action='clone'):
        course = self.get_object(request, unquote(object_id))
        if request.method == 'POST':
            objs, file_name = clone_course(course, request)
            messages.info(request, ugettext('Created %s objects succesfully') % len(objs))
            messages.info(request, ugettext('You have a trace in %s') % file_name)
            return HttpResponseRedirect(reverse('admin:courses_course_change', args=(objs[0].pk,)))
        opts = self.model._meta
        return render_to_response('admin/courses/course/clone_form.html',
                                  {'original': course,
                                   'app_label': opts.app_label,
                                   'opts': opts,
                                   'title': ugettext('Clone Course')},
                                  context_instance=RequestContext(request))


class CourseTeacherAdmin(SortableAdmin):

    """
    CourseTeacher administration panel. Here you can manage the teachers for any
    especified course. Inherits from SortableAdmin, which allows to sort the
    teachers as desired.

    .. versionadded:: 0.1
    """
    raw_id_fields = ('teacher',)
    autocomplete_lookup_fields = {'fk': ['teacher'], }

    list_display = ('course', 'teacher')


class AnnouncementAdmin(MassiveGlobalAdmin):

    """
    Administration for the announcements.

    .. versionadded:: 0.1
    """
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', 'datetime', 'course',)
    list_filter = ('course', )
    subfix_url = 'publish/'
    global_massive_form = MassiveGlobalAnnouncementAdminForm
    global_massive_title = _('Publish announcement massive')
    global_massive_message = _("The announcement was created succesfully")


class UnitAdmin(SortableAdmin):

    """
    Course unit administration. Here you can manage the units themselves, but
    not the nuggets associated with them. Inherits from SortableAdmin, which
    allows to sort the units as desired, ignoring the creation order.

    .. versionadded:: 0.1
    """
    form = UnitForm
    list_display = ('__unicode__', 'unittype', 'start', 'deadline', 'weight')
    list_filter = ('course', )

    class Media:
        js = ("js/unit-admin.js",)


class AttachmentInline(admin.TabularInline):

    """
    Inline for including the attachments in KnowledgeQuantums.

    .. versionadded:: 0.1
    """
    model = Attachment
    form = AttachmentForm


class AttachmentAdmin(admin.ModelAdmin):
    pass


class KnowledgeQuantumAdmin(SortableAdmin):

    """
    Administration for the KnowledgeQuantums. Has an inline for attachments.

    .. versionadded:: 0.1
    """
    inlines = [
        AttachmentInline,
    ]

    list_display = ('__unicode__', 'title', 'media_content_type', 'media_content_id', 'weight')
    list_filter = ('unit', )

csrf_protect_m = method_decorator(csrf_protect)
ensure_csrf_cookie_m = method_decorator(ensure_csrf_cookie)


class QuestionAdmin(admin.ModelAdmin):

    """
    Administration for questions inside nuggets. The URLs are extended to process
    extra stuff like videos and options. It has a get_state, _is_scheduled and
    _is_active method to obtain the current status of the last frame of the video.


    :context: title, object_id, original, is_popup, app_label, opts, has_absolute_url,
              content_type_id, add, change, options_json

    .. versionadded: 0.1
    """
    list_display = ('kq', 'solution_media_content_type', 'solution_media_content_id')
    list_filter = ('solution_media_content_type', )
    search_fields = ('kq__title', 'solution_media_content_id')
    formfield_overrides = {
        models.ImageField: {'widget': ImageReadOnlyWidget},
    }

    def get_urls(self):
        return patterns(
            '',
            url(r'^(.+)/options/$',
                self.admin_site.admin_view(self.edit_options),
                name='courses_question_options'),
            url(r'^(.+)/options/(.+)$',
                self.admin_site.admin_view(self.edit_option),
                name='courses_question_option'),
            url(r'^(.+)/processvideo/$',
                self.admin_site.admin_view(self.process_video),
                name='courses_process_video'),
        ) + super(QuestionAdmin, self).get_urls()

    def get_form(self, request, obj=None, **kwargs):
        form = super(QuestionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['last_frame'].widget.attrs['state'] = self.get_state(obj)
        return form

    def get_state(self, obj=None):
        if obj is None:
            return None

        if obj.last_frame.name == u'':
            inspector = inspect()
            if self._is_scheduled(inspector, obj):
                state = 'scheduled'
            elif self._is_active(inspector, obj):
                state = 'active'
            else:
                state = 'error'
        else:
            state = 'finished'

        return state

    def _is_scheduled(self, inspector, question):
        scheduled = inspector.scheduled()
        if scheduled is None:
            logger.error('Celery seems to be down.')
        else:
            for worker, tasks in scheduled.items():
                for task in tasks:
                    if task['args'] == repr((question, )):
                        return True
        return False

    def _is_active(self, inspector, question):
        active = inspector.active()
        if active is None:
            logger.error('Celery seems to be down.')
        else:
            for worker, tasks in active.items():
                for task in tasks:
                    if task['args'] == repr((question, )):
                        return True
        return False

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['state'] = self.get_state(context.get('original', None))
        return super(QuestionAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    @ensure_csrf_cookie_m
    @csrf_protect_m
    def edit_options(self, request, object_id):
        model = self.model
        opts = model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(ugettext('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

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
                'title': ugettext('Edit options for question'),
                'object_id': object_id,
                'original': obj,
                'is_popup': '_popup' in request.REQUEST,
                'app_label': opts.app_label,
                'opts': opts,
                'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
                'content_type_id': ContentType.objects.get_for_model(self.model).id,
                'add': False,
                'change': True,
                'options_json': simplejson.dumps(json),
            }
            return TemplateResponse(request, [
                "admin/%s/%s/options.html" % (app_label, opts.object_name.lower()),
                "admin/%s/options.html" % app_label,
                "admin/options.html"
            ], context, current_app=self.admin_site.name)

    @csrf_protect_m
    def edit_option(self, request, object_id, option_id):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(ugettext('%(name)s object with primary key %(key)r does not exist.')
                          % {'name': force_unicode(opts.verbose_name),
                             'key': escape(object_id)})

        try:
            option = obj.option_set.get(id=unquote(option_id))
        except ObjectDoesNotExist:
            raise Http404(ugettext('Option %(option)d for question %(question)s does not exist.')
                          % {'option': escape(object_id),
                             'question': escape(option_id)})

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

    @csrf_protect_m
    def process_video(self, request, object_id):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(ugettext('%(name)s object with primary key %(key)r does not exist.')
                          % {'name': force_unicode(opts.verbose_name),
                             'key': escape(object_id)})

        process_video_task.delay(obj.id)

        return HttpResponseRedirect('..')


class OptionAdmin(admin.ModelAdmin):

    """
    Options administration panel.

    .. versionadded:: 0.1
    """
    list_display = ('question', 'x', 'y', 'optiontype')
    list_filter = ('question', )




admin.site.register(Course, CourseAdmin)
admin.site.register(CourseTeacher, CourseTeacherAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(KnowledgeQuantum, KnowledgeQuantumAdmin)
admin.site.register(StaticPage)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Language)
admin.site.register(CourseLanguage)
