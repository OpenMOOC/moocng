# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

import os

from django import forms
from django.forms import ValidationError
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from modeltranslation.forms import TranslationModelForm

from moocng.courses.models import Unit, Attachment, Course, Transcription, get_transcription_types_choices

COURSE_RATING_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]

class CourseForm(TranslationModelForm):

    class Meta:
        model = Course
        exclude = ('students', 'teachers', 'owner')


class UnitForm(forms.ModelForm):

    error_messages = {
        'deadline_missing': _("The deadline date is mandatory for homework and exams."),
        'start_later_deadline': _("The start date is later than the deadline."),
    }

    class Meta:
        model = Unit

    def clean(self):
        start = self.cleaned_data.get('start')
        deadline = self.cleaned_data.get('deadline')

        if self.cleaned_data['unittype'] != u'n' and deadline is None:
            raise ValidationError(self.error_messages['deadline_missing'])

        if start and deadline and start > deadline:
            raise ValidationError(self.error_messages['start_later_deadline'])

        return self.cleaned_data


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment

    def clean_attachment(self):
        file_name, file_ext = os.path.splitext(self.cleaned_data["attachment"].name)
        file_name = slugify(file_name)
        self.cleaned_data["attachment"].name = "%s%s" % (file_name, file_ext)
        attachment = self.cleaned_data.get("attachment", False)
        if attachment:
             if attachment._size > settings.ATTACHMENTS_MAX_SIZE*1024*1024:
                   raise ValidationError("File too large ( > "+settings.ATTACHMENTS_MAX_SIZE+"mb )")
             return attachment

class TranscriptionForm(forms.ModelForm):
    transcription_type = forms.ChoiceField(choices=get_transcription_types_choices(), widget=forms.widgets.Select)
    #language = forms.ChoiceField(choices=,widget=forms.widgets.Select)
    class Meta:
        model = Transcription

    def clean_attachment(self):
        file_name, file_ext = os.path.splitext(self.cleaned_data["filename"].name)
        file_name = slugify(file_name)
        self.cleaned_data["filename"].name = "%s%s" % (file_name, file_ext)
        attachment = self.cleaned_data.get("filename", False)
        if attachment:
             if attachment._size > settings.ATTACHMENTS_MAX_SIZE*1024*1024:
                   raise ValidationError("File too large ( > "+settings.ATTACHMENTS_MAX_SIZE+"mb )")
             return attachment

class ActivityForm(forms.Form):
    course_id = forms.IntegerField(required=True)
    unit_id = forms.IntegerField(required=True)
    kq_id = forms.IntegerField(required=True)

class CourseRatingForm(forms.Form):
    value = forms.ChoiceField(choices=COURSE_RATING_CHOICES, widget=forms.widgets.RadioSelect)

class ForumPostForm(forms.Form):
    postTitle = forms.CharField(required=True, max_length="140", label="", widget=forms.TextInput(attrs={'placeholder': _('Title')}))
    postText = forms.CharField(required=True, max_length="500", label="", widget=forms.Textarea(attrs={'placeholder': _('Write a message...')}))

class ForumReplyForm(forms.Form):
    postText = forms.CharField(required=True, max_length="500", label="", widget=forms.Textarea(attrs={'placeholder': _('Write a message...')}))

class ForumEditForm(forms.Form):
    postText = forms.CharField(required=True, max_length="500", label="", widget=forms.Textarea(attrs={'placeholder': _('Edit your message...')}))
