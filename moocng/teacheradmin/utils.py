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

import logging

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives, EmailMessage
from django.utils.translation import ugettext_lazy as _
from django.template import loader

logger = logging.getLogger(__name__)


def send_invitation(request, invitation):
    subject = _(u'You have been invited to be a teacher in "%s"') % invitation.course.name
    template = 'teacheradmin/email_invitation_teacher.txt'
    context = {
        'host': invitation.host.get_full_name or invitation.host.username,
        'course': invitation.course.name,
        'register': settings.REGISTRY_URL,
        'site': get_current_site(request).name
    }
    to = [invitation.email]
    send_mail_wrapper(subject, template, context, to)


def send_removed_notification(request, email, course):
    subject = _(u'You have been removed as teacher from "%s"') % course.name
    template = 'teacheradmin/email_remove_teacher.txt'
    context = {
        'course': course.name,
        'host': request.user.get_full_name() or request.user.username,
        'site': get_current_site(request).name
    }
    to =  [email]
    send_mail_wrapper(subject, template, context, to)

def send_mail_wrapper(subject, template, context, to):
    try:
        email = EmailMessage(
            subject = subject,
            body = loader.render_to_string(template, context),
            from_email = settings.DEFAULT_FROM_EMAIL,
            to = to
        )
        email.send()
    except IOError as ex:
        logger.error('The notification "%s" to %s could not be sent because of %s' % (subject, str(to), str(ex)))


def send_mass_mail_wrapper(subject, message, recipients, html_content=False):
    mails = []
    content = message
    if html_content:
        content = ""
    for to in recipients:
        email = EmailMultiAlternatives(subject, content, settings.DEFAULT_FROM_EMAIL, [to])
        if html_content:
            email.attach_alternative(message, "text/html")
        mails.append(email)
    try:
        get_connection().send_messages(mails)
    except IOError as ex:
        logger.error('The massive email "%s" to %s could not be sent because of %s' % (subject, recipients, str(ex)))
