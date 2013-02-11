# Copyright 2013 Rooter Analysis S.L.
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
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from moocng.contact.models import CommunicationType


class ContactForm(forms.Form):

    username = forms.CharField(label=_(u'Username'))
    sender = forms.EmailField(label=_(u'Email'))
    communication_type = forms.ModelChoiceField(
        label=_(u'Communication type'),
        required=True,
        queryset=CommunicationType.objects.all(),
        empty_label=None,
        )
    message = forms.CharField(
        label=_(u'Message'),
        widget=forms.Textarea(attrs={'class': 'input-xxlarge'}),
        )
    tos = forms.BooleanField(
        label=mark_safe(_('I have read and agree with the terms of use (<a href="/tos">See Terms of Use</a>)')),
        required=True,
        error_messages={'required': _('You must accept the Terms of Use')},
        )
