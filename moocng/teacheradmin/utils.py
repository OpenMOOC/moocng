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

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _


def send_invitation(request, invitation):
    name = invitation.host.get_full_name() or invitation.host.username
    msg = _(u'Hello, you have been invited to be a teacher in the course "%(course)s" by %(host)s. After your registration in the platform is complete, you will be automatically assigned as a teacher to the course.\n\nYou can register here: %(register)s\n\nBest regards,\n%(site)s\'s team') % {
        'course': invitation.course.name,
        'host': name,
        'register': settings.REGISTRY_URL,
        'site': get_current_site(request).name
    }
    send_mail(_(u'You have been invited to be a teacher in "%s"') %
              invitation.course.name,
              msg,
              settings.DEFAULT_FROM_EMAIL,
              [invitation.email])
