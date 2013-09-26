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

from django import forms
from django.conf import settings
from django.core.files.images import get_image_dimensions
from django.utils.translation import ugettext_lazy as _

from tinymce.widgets import TinyMCE

from moocng.courses.forms import AnnouncementForm as CoursesAnnouncementForm
from moocng.courses.models import Course
from moocng.forms import (BootstrapMixin, BootstrapClearableFileInput,
                          HTML5DateInput, BootstrapInlineRadioSelect)
from moocng.teacheradmin.models import MassiveEmail
from moocng.media_contents import media_content_extract_id

from moocng.assets.models import Asset


class CourseForm(forms.ModelForm):

    """
    Course form. Make some changes to the form classes and clean the media fields
    to prevent errors processing the content.

    :returns: HTML Form

    ..versionadded:: 0.1
    """
    class Meta:
        model = Course
        exclude = ('slug', 'teachers', 'owner', 'students')
        widgets = {
            'start_date': HTML5DateInput(),
            'end_date': HTML5DateInput(),
            'certification_banner': BootstrapClearableFileInput(),
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

    def clean_main_image(self):
        main_image = self.cleaned_data.get("main_image")
        if main_image:
           w, h = get_image_dimensions(main_image)
           if w != settings.COURSE_MAIN_IMAGE_MAX_WIDTH:
               raise forms.ValidationError("Uploaded main image is %i pixel wide. Maximun width for main image is %ipx" % (w, settings.COURSE_MAIN_IMAGE_MAX_WIDTH))
           if h != settings.COURSE_MAIN_IMAGE_MAX_HEIGHT:
               raise forms.ValidationError("Uploaded main image is %i pixel high. Maximun height for main image is %ipx" % (h, settings.COURSE_MAIN_IMAGE_MAX_HEIGHT))
        return main_image

class AnnouncementForm(CoursesAnnouncementForm, BootstrapMixin):

    """
    Announcement form. Inherits from CoursesAnnouncementForm and adds a send_email
    field.

    :returns: HTML Form

    .. versionadded:: 0.1
    """

    send_email = forms.BooleanField(
        required=False,
        label=_(u'Send the announcement via email to all the students in this course'),
        initial=False,
        help_text=_(u'Please use this with caution as some courses has many students'),
    )


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


class MassiveEmailForm(forms.ModelForm, BootstrapMixin):

    """
    Massive email model form. Adapts subject and message fields size.

    :returns: HTML Form

    .. versionadded:: 0.1
    """
    class Meta:
        model = MassiveEmail
        exclude = ('course', )
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'message': TinyMCE(attrs={'class': 'input-xxlarge'}),
        }
