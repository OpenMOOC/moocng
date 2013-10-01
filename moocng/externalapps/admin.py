# -*- coding: utf-8 -*-
from django.contrib import admin

from moocng.externalapps.models import ExternalApp, EXTERNAL_APPS_QUEUE
from moocng.externalapps.tasks import process_instance_creation


class ExternalAppAdmin(admin.ModelAdmin):
    fields = (
            'app_name',
            'ip_address',
            'slug',
            'instance_type',
            'url_link',
            'status',
            'visibility',
            'course',
            'execute_task_on_save',
    )
    readonly_fields=('url_link',)
    list_display = ('app_name', 'ip_address', 'instance_type', 'url', 'status', 'course', 'visibility',)
    list_filter = ('app_name', 'ip_address', 'status', 'course', 'visibility',)

    def save_model(self, request, obj, form, change):
        if change and obj.execute_task_on_save:
                process_instance_creation.apply_async(
                    args=[obj.id],
                    queue=EXTERNAL_APPS_QUEUE
                )
        super(ExternalAppAdmin, self).save_model(request, obj, form, change)

admin.site.register(ExternalApp, ExternalAppAdmin)
