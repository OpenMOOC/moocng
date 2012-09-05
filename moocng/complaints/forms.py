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

COMUNICATION_TYPE = (('rights','Rights violation'),
                     ('feedback','Feedback / Comments'),
                     ('unsubscribe','Remove account'),
                     ('other','Other'))

class ComplaintsForm(forms.Form):
    username = forms.CharField(label='Username')
    sender = forms.EmailField(label='Email')
    communication_type = forms.ChoiceField(label='Communication type', choices=COMUNICATION_TYPE)
    message = forms.CharField(label='Message', widget=forms.Textarea())
    tos = forms.BooleanField(label="",
                            required=True, 
                            help_text='I have read and agree with the terms of service (<a href="/tos">See Terms of Use</a>)', 
                            error_messages={'required':'You must accept the Terms of Use'})
