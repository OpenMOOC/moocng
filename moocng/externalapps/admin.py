# -*- coding: utf-8 -*-
from django.contrib import admin

from moocng.externalapps.models import ExternalApp, EXTERNAL_APPS_QUEUE
from moocng.externalapps.tasks import process_instance_creation


class ExternalAppAdmin(admin.ModelAdmin):
    #readonly_fields=('ip_address', 'app_name', 'base_url', 'status',)
    list_display = ('app_name', 'ip_address', 'status', 'slug', 'course', 'visibility',)
    list_filter = ('app_name', 'ip_address', 'status', 'course', 'visibility',)

    def save_model(self, request, obj, form, change):
        if change and obj.execute_task_on_save:
                process_instance_creation.apply_async(
                    args=[obj.id],
                    queue=EXTERNAL_APPS_QUEUE
                )
        super(ExternalAppAdmin, self).save_model(request, obj, form, change)

admin.site.register(ExternalApp, ExternalAppAdmin)

"""
from django.contrib import admin
from django.db.models import signals

from moocng.externalapps.models import ExternalApp, on_process_instance_creation


class ExternalAppAdmin(admin.ModelAdmin):
    #readonly_fields=('ip_address', 'app_name', 'base_url', 'status',)
    list_display = ('app_name', 'ip_address', 'status', 'slug', 'course', 'visibility',)
    list_filter = ('app_name', 'ip_address', 'status', 'course', 'visibility',)

    def save_model(self, request, obj, form, change):
        if obj.execute_task_on_save:
            obj.save()
        else:
            signals.post_save.disconnect(receiver=on_process_instance_creation, sender=ExternalApp)
            obj.save()
            signals.post_save.connect(on_process_instance_creation, sender=ExternalApp)

admin.site.register(ExternalApp, ExternalAppAdmin)
"""
