# Copyright 2012 Rooter Analysis S.L.
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

from moocng.teacheradmin.models import Invitation, MassiveEmail


class InvitationAdmin(admin.ModelAdmin):

    list_display = ('course', 'email', 'datetime')
    list_filter = ('course', )


class MassiveEmailAdmin(admin.ModelAdmin):

    list_display = ('course', 'subject', 'datetime')
    list_filter = ('course', )


admin.site.register(Invitation, InvitationAdmin)
admin.site.register(MassiveEmail, MassiveEmailAdmin)
