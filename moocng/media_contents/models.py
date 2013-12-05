# -*- coding: utf-8 -*-
# Copyright 2013 Pablo Martín
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


def monkey_patching_update_maxlength_of_field(field, new_max_length):
    from django.core.validators import MaxLengthValidator
    field.max_length = new_max_length
    for validator in field.validators:
        if isinstance(validator, MaxLengthValidator):
            validator.limit_value = new_max_length


def monkey_patching_update_user_maxlength():
    MAX_EMAIL_LENGTH = 254
    from django.contrib.auth.models import User
    username_field = User._meta.get_field_by_name('username')[0]
    monkey_patching_update_maxlength_of_field(username_field, MAX_EMAIL_LENGTH)

    from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
    for form_class in (UserCreationForm, UserChangeForm, AuthenticationForm):
        username_field = form_class.base_fields['username']
        monkey_patching_update_maxlength_of_field(username_field, MAX_EMAIL_LENGTH)
        username_field.widget.attrs['maxlength'] = MAX_EMAIL_LENGTH
        username_field.widget.attrs['class'] = 'vTextField'
        username_field.help_text = ''

    email_field = User._meta.get_field_by_name('email')[0]
    monkey_patching_update_maxlength_of_field(email_field, MAX_EMAIL_LENGTH)

    first_name_field = User._meta.get_field_by_name('first_name')[0]
    monkey_patching_update_maxlength_of_field(first_name_field, 100)

    last_name_field = User._meta.get_field_by_name('last_name')[0]
    monkey_patching_update_maxlength_of_field(last_name_field, 100)

monkey_patching_update_user_maxlength()
