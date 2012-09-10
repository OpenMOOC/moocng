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

from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Unit


class UnitForm(ModelForm):

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
