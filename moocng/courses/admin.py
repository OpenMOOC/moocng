# Copyright 2012 Rooter Analysis S.L. All rights reserved.
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

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import models
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from adminsortable.admin import SortableAdmin

from moocng.courses.models import Course, Announcement, Unit, KnowledgeQuantum
from moocng.courses.models import Question, Option, Attachment
from moocng.courses.widgets import ImageReadOnlyWidget


class CourseAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name', )}


class AnnouncementAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title', )}
    list_display = ('course', 'title', 'datetime')
    list_filter = ('course', )


class UnitAdmin(SortableAdmin):

    list_display = ('__unicode__', 'unittype', 'deadline')
    list_filter = ('course', )


class AttachmentInline(admin.TabularInline):
    model = Attachment


class KnowledgeQuantumAdmin(SortableAdmin):

    inlines = [
        AttachmentInline,
    ]

    list_display = ('__unicode__', 'title', 'video')
    list_filter = ('unit', )


csrf_protect_m = method_decorator(csrf_protect)
ensure_csrf_cookie_m = method_decorator(ensure_csrf_cookie)


class QuestionAdmin(admin.ModelAdmin):

    list_display = ('kq', 'solution')
    list_filter = ('kq', )
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
            ) + super(QuestionAdmin, self).get_urls()

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
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

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
                    'x': opt.x, 'y': opt.y,
                    'width': opt.width, 'height': opt.height,
                    } for opt in obj.option_set.all()]
            context = {
                'title': _('Edit options for question'),
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
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.')
                          % {'name': force_unicode(opts.verbose_name),
                             'key': escape(object_id)})

        try:
            option = obj.option_set.get(id=unquote(option_id))
        except ObjectDoesNotExist:
            raise Http404(_('Option %(option)d for question %(question)s does not exist.')
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
                'x': option.x, 'y': option.y,
                'width': option.width, 'height': option.height,
                }
            return HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')


class OptionAdmin(admin.ModelAdmin):

    list_display = ('question', 'x', 'y', 'optiontype')
    list_filter = ('question', )


admin.site.register(Course, CourseAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(KnowledgeQuantum, KnowledgeQuantumAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)
