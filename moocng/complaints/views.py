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

from django.core.mail import mail_admins
from django.http import HttpResponseRedirect
from django.shortcuts import render
from moocng.complaints.forms import ComplaintsForm


def complaints(request):
    if request.method == 'POST':
        form = ComplaintsForm(request.POST)
        if form.is_valid():
            communication_type = form.cleaned_data['communication_type']
            subject = "%s | %s <%s>" % (communication_type.title(),
                                        form.cleaned_data['username'],
                                        form.cleaned_data['sender'])
            message = form.cleaned_data['message']
            mail_admins(subject, message)
            return HttpResponseRedirect('/complaints/sent')
    else:
        if request.user.is_authenticated():
            full_name = request.user.get_full_name()
            if full_name:
                name = "%s (%s)" % (request.user.username, full_name)
            else:
                name = request.user.username
            initial = {
                "username": name,
                "sender": request.user.email,
            }
        else:
            initial = {}
        form = ComplaintsForm(initial=initial)

    return render(request, 'complaints.html', {
        'form': form,
    })


def sent(request):
    return render(request, 'complaints_sent.html')
