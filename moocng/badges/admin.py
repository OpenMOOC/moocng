# -*- coding: utf-8 -*-

# Copyright 2012 UNED
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

from moocng.badges.models import (Badge, Award, Revocation, Alignment, Tag,
                                  Identity)


def show_image(obj):
    if isinstance(obj, Badge):
        url = obj.image.url if obj.image else None
    else:
        url = obj.badge.image.url if obj.badge and obj.badge.image else None
    return '<img src="%s" width="30" height="30" />' % url


show_image.allow_tags = True
show_image.short_description = _("Image")


class BadgeAdmin(admin.ModelAdmin):
    model = Badge
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', show_image, 'created',)


class AwardAdmin(admin.ModelAdmin):
    model = Award
    raw_id_fields = ('user',)
    autocomplete_lookup_fields = {'fk': ['user']}
    list_display = ('user', 'badge', show_image, 'awarded', 'revoked')
    search_fields = ('uuid', 'user__username')


class RevocationAdmin(admin.ModelAdmin):
    model = Revocation
    raw_id_fields = ('award',)
    autocomplete_lookup_fields = {'fk': ['award']}
    list_display = ('award', 'reason',)


class AlignmentAdmin(admin.ModelAdmin):
    model = Alignment
    list_display = ('name', 'url')


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name',)


class IdentityAdmin(admin.ModelAdmin):
    model = Identity
    search_fields = ('user__username', )
    raw_id_fields = ('user',)
    autocomplete_lookup_fields = {'fk': ['user']}
    list_display = ('user', 'type', 'identity_hash', 'hashed', 'salt')


admin.site.register(Badge, BadgeAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(Revocation, RevocationAdmin)
admin.site.register(Alignment, AlignmentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Identity, IdentityAdmin)
