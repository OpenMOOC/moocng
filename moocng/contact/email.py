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

import logging

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives


logger = logging.getLogger(__name__)


def send_contact_message(communication_type, sender_username, sender_email,
                         message, fail_silently=False, connection=None):

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

    mail = EmailMultiAlternatives(
        u'%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject),
        message,
        settings.SERVER_EMAIL,
        to,
        connection=connection,
        headers=headers,
        )
    mail.send(fail_silently=fail_silently)

