from django.contrib import admin

from adminsortable.admin import SortableAdmin

from moocng.courses.models import Course, Announcement, Unit, KnowledgeQuantum
from moocng.courses.models import Question, Option


class CourseAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name', )}


class AnnouncementAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title', )}
    list_display = ('course', 'title', 'datetime')


class UnitAdmin(SortableAdmin):

    list_display = ('course', 'title', 'unittype', 'deadline')


class KnowledgeQuantumAdmin(admin.ModelAdmin):

    list_display = ('unit', 'title', 'video')


class QuestionAdmin(admin.ModelAdmin):

    list_display = ('kq', 'solution')


class OptionAdmin(admin.ModelAdmin):

    list_display = ('question', 'x', 'y', 'optiontype')


admin.site.register(Course, CourseAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(KnowledgeQuantum, KnowledgeQuantumAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)
