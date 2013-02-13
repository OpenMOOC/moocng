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

from django import forms
from django.forms.util import ErrorDict
from django.utils.translation import ugettext as _

from tinymce.widgets import TinyMCE

from moocng.courses.models import Course
from moocng.teacheradmin.models import MassiveEmail


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        exclude = ('slug', 'teachers', 'owner', 'students')

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.widgets.TextInput):
                widget.attrs['class'] = 'input-xlarge'

            elif isinstance(widget, forms.widgets.DateInput):
                widget.attrs['class'] = 'input-xlarge'
                widget.attrs['placeholder'] = 'YYYY-MM-DD'

            elif isinstance(widget, forms.widgets.Textarea):
                widget.mce_attrs['width'] = '780'  # bootstrap span10

            elif isinstance(widget, forms.widgets.ClearableFileInput):
                # In bootstrap the <input checkbox> must be inside the <label>
                widget.template_with_clear = u'<label for="%(clear_checkbox_id)s">%(clear)s %(clear_checkbox_label)s</label>'

class MassiveEmailForm(forms.ModelForm):

    subject = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'span10',
            'maxlength': 100,
        }), label=_('Subject'))
    message = forms.CharField(widget=TinyMCE(
        attrs={
            'class': 'span10',
        }), label=_('Message'))

    class Meta:
        model = MassiveEmail
        exclude = ('course', 'datetime')
