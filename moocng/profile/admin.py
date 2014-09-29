# -*- coding: utf-8 -*-
# Copyright 2013 UNED
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
from django import forms
from django.contrib.auth.forms import UserChangeForm 
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from moocng.profile.models import UserProfile,Organization

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1
    raw_id_fields = ('last_announcement',)
    autocomplete_lookup_fields = {'fk': ['last_announcement'], }

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Organization)

