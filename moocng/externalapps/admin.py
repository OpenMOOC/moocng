# -*- coding: utf-8 -*-
from django.contrib import admin

from moocng.externalapps.models import ExternalApp


class ExternalAppAdmin(admin.ModelAdmin):
    readonly_fields=('name', 'base_url', 'status')

admin.site.register(ExternalApp, ExternalAppAdmin)
