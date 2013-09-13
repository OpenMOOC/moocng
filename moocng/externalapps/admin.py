# -*- coding: utf-8 -*-
from django.contrib import admin

from moocng.externalapps.models import ExternalApp


class ExternalAppAdmin(admin.ModelAdmin):
    #readonly_fields=('ip_address', 'app_name', 'base_url', 'status',)
    list_display = ('app_name', 'ip_address', 'status',)
    list_filter = ('app_name', 'ip_address', 'status',)

admin.site.register(ExternalApp, ExternalAppAdmin)
