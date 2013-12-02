# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from moocng.admin import MassiveGlobalAdmin
from moocng.teacheradmin.forms import MassiveGlobalEmailAdminForm
from moocng.teacheradmin.models import Invitation, MassiveEmail


class InvitationAdmin(admin.ModelAdmin):

    """
    Invitation model administration for Moocng.

    .. versionadded:: 0.1
    """
    raw_id_fields = ('host',)
    autocomplete_lookup_fields = {'fk': ['host'], }

    list_display = ('course', 'email', 'datetime')
    list_filter = ('course', )


class MassiveEmailAdmin(MassiveGlobalAdmin):

    """
    MassiveEmail model administration.

    .. versionadded:: 0.1
    """

    list_display = ('subject', 'datetime', 'course')
    list_filter = ('course', )
    global_massive_form = MassiveGlobalEmailAdminForm
    global_massive_title = _('Send email massive')
    global_massive_message = _("The email has been queued. The emails will be sent soon")
    subfix_url = 'send/'


admin.site.register(Invitation, InvitationAdmin)
admin.site.register(MassiveEmail, MassiveEmailAdmin)
