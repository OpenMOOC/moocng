# Copyright 2013 UNED
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
from django.core.mail.message import EmailMultiAlternatives
from django.utils.translation import ugettext as _
import re


logger = logging.getLogger(__name__)


def send_contact_message(communication_type, course, sender_username, sender_email,
                         message, fail_silently=False, connection=None):

    # Add course name to the message body
    message = "%s: %s\n\n%s" % (_("Course"), course, message)

    subject = "%s | %s <%s>" % (communication_type.title,
                                sender_username,
                                sender_email)
    headers = {'Reply-To': sender_email}

    destination = communication_type.destination
    if not destination:
        if not settings.MANAGERS:
            logger.error('Could not send a contact message because there is no destination email configured neither in the communication type or the MANAGERS setting.')
            return
        else:
            to = [m[1] for m in settings.MANAGERS]
    else:
        to = [destination]

    try:
        if settings.SEND_CONTACT_EMAIL_FROM_SENDER:
            from_ = sender_email
        else:
            from_ = settings.DEFAULT_FROM_EMAIL
    except AttributeError:
        from_ = settings.DEFAULT_FROM_EMAIL

    mail = EmailMultiAlternatives(
        u'%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject),
        message,
        from_,
        to,
        connection=connection,
        headers=headers,
    )
    mail.send(fail_silently=fail_silently)

def send_support_message(subject, body, url, user, device, position, date, timezone, fail_silently=False, connection=None):
    headers = { 'Reply-To': user.email }
    mail_subject = "%s - %s" % (settings.SUPPORT_SUBJECT_PREFIX, subject)
    mail_body = "Message:\n%s\n" % (body)
    m = re.search('^http(s)?:\/\/[a-z0-9-]+(\.[a-z0-9-]+)*?(:[0-9]+)?(\/)?.([a-z]+)/', url)
    base_url = m.group(0)
    mail_extrainfo = (  "-----------\n"
                        "Username: %s (%suser/profile/%s)\n"
                        "User real name: %s\n"
                        "User id: %s (%sadmin/auth/user/%s/)\n"
                        "User email: %s\n"
                        "Related URL: %s\n"
                        "Contact date: %s\n"
                        "User geoposition: %s(%s,%s) (http://maps.google.com/maps?q=%s,%s)\n"
                        "Timezone: %s\n"
                        "Device type: %s (%s)\n"
                        "Browser: %s (%s)\n") % ( user.username, base_url, user.username,
                        user.get_full_name(),
                        user.id, base_url, user.id,
                        user.email,
                        url,
                        date,
                        position['location'], position['latitude'], position['longitude'],
                        position['latitude'], position['longitude'],
                        timezone,
                        device['type'], device['os'],
                        device['browser'], device['orientation'])
    destination = [settings.SUPPORT_EMAIL]
    origin = user.email

    mail = EmailMultiAlternatives(
        mail_subject,
        u'%s%s' % (mail_body, mail_extrainfo),
        origin,
        destination,
        connection=connection,
        headers=headers,
    )
    mail.send(fail_silently=fail_silently)
