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

from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class ImageReadOnlyWidget(Widget):

    """
    Show the status of the last_frame process.

    :returns: String

    .. versionadded:: 0.1
    """

    def render(self, name, value, attrs=None):
        if value is None:
            return u''  # the question is not saved yet
        elif value.name == u'':
            state = self.attrs.get('state', None)
            if state == 'error':
                return _(u'There has been a problem downloading the video. Please check the logs')
            elif state == 'scheduled':
                return _(u'The video is about to be downloaded. Please be patient')
            elif state == 'active':
                return _(u'The video is being downloaded at this moment. Please be patient')
            else:
                return _(u'Unknown error')
        else:
            return mark_safe(u'<img src="%s" />' % value.url)
