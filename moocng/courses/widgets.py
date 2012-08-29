# Copyright 2012 Rooter Analysis S.L. All rights reserved.
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

from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

class ImageReadOnlyWidget(Widget):

    def render(self, name, value, attrs=None):
        if value is not None:
            return mark_safe(u'<img src="%s" />' % value.url)
        else:
            return u''
