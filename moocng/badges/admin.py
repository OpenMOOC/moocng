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
from django.utils.translation import ugettext_lazy as _

from moocng.badges.models import Badge, Award


def show_image(obj):
    if isinstance(obj, Badge):
        url = obj.image.url
    else:
        url = obj.badge.image.url
    return '<img src="%s" width="30" height="30" />' % url


show_image.allow_tags = True
show_image.short_description = _("Image")


class BadgeAdmin(admin.ModelAdmin):
    model = Badge
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', show_image, 'created',)


class AwardAdmin(admin.ModelAdmin):
    model = Award
    list_display = ('user', 'badge', show_image, 'awarded',)


admin.site.register(Badge, BadgeAdmin)
admin.site.register(Award, AwardAdmin)
