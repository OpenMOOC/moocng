from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from adminsortable.admin import SortableAdmin

from moocng.courses.models import Course, Announcement, Unit, KnowledgeQuantum
from moocng.courses.models import Question, Option


class CourseAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name', )}


class AnnouncementAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title', )}
    list_display = ('course', 'title', 'datetime')
    list_filter = ('course', )


class UnitAdmin(SortableAdmin):

    list_display = ('__unicode__', 'unittype', 'deadline')
    list_filter = ('course', )


class KnowledgeQuantumAdmin(SortableAdmin):

    list_display = ('__unicode__', 'title', 'video')
    list_filter = ('unit', )


csrf_protect_m = method_decorator(csrf_protect)


class QuestionAdmin(admin.ModelAdmin):

    list_display = ('kq', 'solution')
    list_filter = ('kq', )
    readonly_fields = ('last_frame', )

    def get_urls(self):
        return patterns(
            '',
            url(r'^(.+)/options/$',
                self.admin_site.admin_view(self.edit_options),
                name='courses_question_options'),
            ) + super(QuestionAdmin, self).get_urls()

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
            }
        return TemplateResponse(request, [
                "admin/%s/%s/options.html" % (app_label, opts.object_name.lower()),
                "admin/%s/options.html" % app_label,
                "admin/options.html"
                ], context, current_app=self.admin_site.name)
        return HttpResponse('ok')



class OptionAdmin(admin.ModelAdmin):

    list_display = ('question', 'x', 'y', 'optiontype')
    list_filter = ('question', )


admin.site.register(Course, CourseAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(KnowledgeQuantum, KnowledgeQuantumAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)
