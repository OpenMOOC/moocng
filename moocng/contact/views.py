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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import View

from moocng.contact.forms import ContactForm
from moocng.contact.email import send_contact_message


class Contact(View):
    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            sender = form.cleaned_data['sender']
            if request.user.is_authenticated():
                sender = request.user.email

            send_contact_message(form.cleaned_data['communication_type'],
                                 form.cleaned_data['course'],
                                 form.cleaned_data['username'],
                                 sender,
                                 form.cleaned_data['message'])
            messages.success(request, _(u'Thank you for contacting us. The provided information will be sent to the appropiate staff. We will contact you soon to tell you about the state of your request.'))
            return HttpResponseRedirect(reverse('home'))
        return render(request, 'contact/contact.html', {
            'form': form,
        })

    def get(self, request):
        initial = {}
        if request.user.is_authenticated():
            name = ''
            full_name = request.user.get_full_name()
            if full_name:
                name = full_name
            if request.user.username != request.user.email:
                if name:
                    name += " (%s)" % request.user.username
                else:
                    name = request.user.username
            initial = {
                "username": name,
                "sender": request.user.email,
            }

        form = ContactForm(initial=initial)

        return render(request, 'contact/contact.html', {
            'form': form,
        })
