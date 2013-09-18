# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db.models import signals

from moocng.externalapps.models import ExternalApp, on_process_instance_creation


class ExternalAppAdmin(admin.ModelAdmin):
    #readonly_fields=('ip_address', 'app_name', 'base_url', 'status',)
    list_display = ('app_name', 'ip_address', 'status', 'slug',)
    list_filter = ('app_name', 'ip_address', 'status',)

    def save_model(self, request, obj, form, change):
        if obj.execute_task_on_save:
            obj.save()
        else:
            signals.post_save.disconnect(receiver=on_process_instance_creation, sender=ExternalApp)
            obj.save()
            signals.post_save.connect(on_process_instance_creation, sender=ExternalApp)

admin.site.register(ExternalApp, ExternalAppAdmin)
