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

from django.forms import ModelForm
from django.forms.util import ErrorDict

from moocng.courses.models import Course


class CourseForm(ModelForm):

    class Meta:
        model = Course
        exclude = ('slug', 'teachers', 'owner', 'students')

    def get_pretty_errors(self):
        errors = ErrorDict()
        for k, v in self.errors.items():
            name = self.fields[k].label
            errors[name] = v
        return errors
