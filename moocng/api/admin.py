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

import logging
import uuid

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


from adminsortable.admin import SortableAdmin

from moocng.api.models import UserApi

logger = logging.getLogger(__name__)


class UserApiAdmin(SortableAdmin):
    raw_id_fields = ('user',)
    autocomplete_lookup_fields = { 'fk': ['user'], }

    readonly_fields = ('key',)
    actions = ['change_key']

    def change_key(self, request, queryset):
        for apikey in queryset:
            apikey.key = unicode(uuid.uuid4())
            apikey.save()

    change_key.short_description = _("Change key of selected %(verbose_name_plural)s")

admin.site.register(UserApi, UserApiAdmin)
