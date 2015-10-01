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

from django import forms
from django.conf import settings
from django.core.files.images import get_image_dimensions
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from modeltranslation.forms import TranslationModelForm

from tinymce.widgets import TinyMCE

from moocng.courses.models import Announcement
from moocng.courses.models import Course, StaticPage
from moocng.forms import (BootstrapMixin, BootstrapClearableFileInput,
                          HTML5DateInput, BootstrapInlineRadioSelect)
from moocng.teacheradmin.models import MassiveEmail
from moocng.teacheradmin.tasks import send_massive_email_task
from moocng.media_contents import media_content_extract_id

from moocng.assets.models import Asset


class CourseForm(TranslationModelForm):

    """
    Course form. Make some changes to the form classes and clean the media fields
    to prevent errors processing the content.

    :returns: HTML Form

    ..versionadded:: 0.1
    """
    error_messages = {
        'invalid_image': _('Image must be {0}px x {1}px').format(Course.THUMBNAIL_WIDTH, Course.THUMBNAIL_HEIGHT),
        'file_too_big': _('Image size must be less than {0}Mb').format(settings.ATTACHMENTS_MAX_SIZE),
    }

    class Meta:
        model = Course
        exclude = ('slug', 'teachers', 'owner', 'students',
                   'max_mass_emails_month', 'created_from',
                   'is_activity_clonable','group_max_size', 'has_groups', 'forum_slug', 'official_course')
        widgets = {
            'start_date': HTML5DateInput(),
            'end_date': HTML5DateInput(),
            #'certification_file': BootstrapClearableFileInput(),
            'status': BootstrapInlineRadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.DateInput)):
                widget.attrs['class'] = 'input-xlarge'

            elif isinstance(widget, forms.widgets.Textarea):
                widget.mce_attrs['width'] = '780'  # bootstrap span10

    def clean_promotion_media_content_id(self):
        content_type = self.data.get('promotion_media_content_type')
        content_id = self.data.get('promotion_media_content_id')
        if content_type and content_id:
            if not media_content_extract_id(content_type, content_id):
                raise forms.ValidationError(_('Invalid content id or url'))
        elif content_type and not content_id:
            raise forms.ValidationError(_('Invalid content id or url'))
        return content_id

    def clean_promotion_media_content_type(self):
        content_type = self.data.get('promotion_media_content_type')
        content_id = self.data.get('promotion_media_content_id')
        if content_id and not content_type:
            raise forms.ValidationError(_('You must select a content type or remove the content id'))
        return content_type

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get("thumbnail")
        if thumbnail and 'size' in thumbnail:
            if thumbnail._size > settings.ATTACHMENTS_MAX_SIZE*1024*1024:
                raise forms.ValidationError(self.error_messages['file_too_big'])
            w, h = get_image_dimensions(thumbnail)
            if w < Course.THUMBNAIL_WIDTH or h < Course.THUMBNAIL_HEIGHT:
                raise forms.ValidationError(self.error_messages['invalid_image'])
        return thumbnail

    def clean_background(self):
        background = self.cleaned_data.get("background")
        if background and 'size' in background:
            if background._size > settings.ATTACHMENTS_MAX_SIZE*1024*1024:
                raise forms.ValidationError(self.error_messages['file_too_big'])
            w, h = get_image_dimensions(background)
            if w < Course.THUMBNAIL_WIDTH or h < Course.THUMBNAIL_HEIGHT:
                raise forms.ValidationError(self.error_messages['invalid_image'])
        return background

    def clean(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        print start_date
        print end_date
        if start_date >= end_date:
            raise forms.ValidationError(_('Start date must be lower than end date'))
        return self.cleaned_data


class GroupsForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['has_groups', 'group_max_size']


class BaseAnnouncementForm(forms.ModelForm):

    send_email = forms.BooleanField(
        required=False,
        label='',
        initial=False,
    )

    def save(self, commit=True):
        instance = super(BaseAnnouncementForm, self).save(commit=False)
        if not 'slug' in self.fields:
            slug = slugify(instance.title)
            max_length = instance._meta.get_field_by_name('slug')[0].max_length
            if len(slug) >= max_length:
                slug = slug[:max_length - 1]
            instance.slug = slug
        instance.course = getattr(self, 'course', None)
        if commit:
            instance.save()
        if self.cleaned_data.get('send_email', None):
            me = MassiveEmail.objects.create_from_announcement(instance, massive_email_type=self.massive_email_type)
            me.send_in_batches(send_massive_email_task)
        return instance


class AnnouncementForm(BaseAnnouncementForm, BootstrapMixin):

    """
    Announcement form. Inherits from CoursesAnnouncementForm and adds a send_email
    field.

    :returns: HTML Form

    .. versionadded:: 0.1
    """
    massive_email_type = 'course'

    class Meta:
        model = Announcement
        exclude = ('slug', 'course',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'content': TinyMCE(attrs={'class': 'input-xxlarge'}),
        }

    def __init__(self, course, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.course = course
        self.fields['send_email'].label = _(u'Send the announcement via email to all the students in this course')
        self.fields['send_email'].help_text = _(u'Please use this with caution as some courses has many students')

    def remain_send_emails(self, massive_emails):
        num_recent_massive_emails = massive_emails.recents().count()
        remain_send = self.course.max_mass_emails_month - num_recent_massive_emails
        if remain_send < 1:
            del self.fields['send_email']
        return remain_send


class MassiveGlobalAnnouncementAdminForm(BaseAnnouncementForm):

    massive_email_type = 'all'
    check_email = forms.BooleanField(label='', widget=forms.HiddenInput, required=False)

    class Meta:
        model = Announcement
        exclude = ('course',)

    def __init__(self, *args, **kwargs):
        super(MassiveGlobalAnnouncementAdminForm, self).__init__(*args, **kwargs)
        self.fields['send_email'].label = _(u'Send the announcement via email to all users')
        self.fields['send_email'].help_text = _(u'Please use this with caution there are a lot of users')

    def clean(self):
        cleaned_data = super(MassiveGlobalAnnouncementAdminForm, self).clean()
        if not self.errors and self.cleaned_data.get('send_email', None) and not cleaned_data.get('check_email', None):
            recipients = MassiveEmail.get_recipients_classmethod('all', None)
            self.fields['check_email'].widget = forms.CheckboxInput()
            self.fields['check_email'].label = _('Yes, I want send %s emails') % recipients.count()
            raise forms.ValidationError(_('This action send %s emails, are you sure? Please check in the last checkbox') % recipients.count())
        return cleaned_data


class AssetTeacherForm(forms.ModelForm, BootstrapMixin):

    """
    AssetTeacher model form

    :returns: HTML Form

    .. versionadded:: 0.1
    """
    class Meta:
        model = Asset
        exclude = ('slot_duration', 'max_bookable_slots', 'reservation_in_advance',
                   'cancelation_in_advance',)


class BaseMassiveEmailForm(forms.ModelForm):

    def save(self, commit=True):
        instance = super(BaseMassiveEmailForm, self).save(commit=False)
        if getattr(self, 'course', None):
            instance.course = self.course
            instance.massive_email_type = 'course'
            instance.subject = "%s - %s" % (self.course.name, instance.subject)
        instance.save()
        instance.send_in_batches(send_massive_email_task)
        return instance


class MassiveEmailForm(BaseMassiveEmailForm, BootstrapMixin):

    """
    Massive email model form. Adapts subject and message fields size.

    :returns: HTML Form

    .. versionadded:: 0.1
    """
    class Meta:
        model = MassiveEmail
        exclude = ('course', 'massive_email_type')
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'message': TinyMCE(attrs={'class': 'input-xxlarge'}),
        }

    def __init__(self, course, *args, **kwargs):
        super(MassiveEmailForm, self).__init__(*args, **kwargs)
        self.course = course

    def remain_send_emails(self, massive_emails):
        num_recent_massive_emails = massive_emails.recents().count()
        remain_send = self.course.max_mass_emails_month - num_recent_massive_emails
        if remain_send < 1:
            self.fields['subject'].widget.attrs['readonly'] = 'readonly'
            self.fields['message'].widget.mce_attrs['readonly'] = 1
        return remain_send


class MassiveGlobalEmailAdminForm(BaseMassiveEmailForm):

    check_email = forms.BooleanField(label='', widget=forms.HiddenInput, required=False)

    class Meta:
        model = MassiveEmail
        exclude = ('course',)
        widgets = {
            'massive_email_type': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(MassiveGlobalEmailAdminForm, self).__init__(*args, **kwargs)
        massive_email_type_choices = dict(self.fields['massive_email_type'].choices)
        del massive_email_type_choices['course']
        self.fields['massive_email_type'].choices = massive_email_type_choices.items()

    def clean(self):
        cleaned_data = super(MassiveGlobalEmailAdminForm, self).clean()
        if not self.errors and not cleaned_data.get('check_email', None):
            recipients = MassiveEmail.get_recipients_classmethod(cleaned_data['massive_email_type'], None)
            self.fields['check_email'].widget = forms.CheckboxInput()
            self.fields['check_email'].label = _('Yes, I want send %s emails') % recipients.count()
            raise forms.ValidationError(_('This action send %s emails, are you sure? Please check in the last checkbox') % recipients.count())
        return cleaned_data


class StaticPageForm(TranslationModelForm, BootstrapMixin):

    class Meta:
        model = StaticPage
        include = ('title', 'body',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'wide'}),
            'body': TinyMCE(attrs={'class': 'wide'}),
        }

    def __init__(self, *args, **kwargs):
        super(StaticPageForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.DateInput)):
                widget.attrs['class'] = 'wide'
            elif isinstance(widget, forms.widgets.Textarea):
                widget.mce_attrs['width'] = '780'  # bootstrap span10



# class BadgesForm(forms.Form):
#     badgeTitle = forms.CharField(required=True)
#     noteBadge = forms.CharField(required=True)
#     unitBadge = forms.ChoiceField(widget=forms.Select, required=False, choices=[])
