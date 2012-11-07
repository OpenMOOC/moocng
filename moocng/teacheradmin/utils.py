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
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

def send_invitation(invitation):
    import ipdb;ipdb.set_trace()
    msg = (u'Hello, you have been invited to be a teacher in the course %s by '
           u'%s. After your registration in the platform is complete, you '
           u'will be automatically assigned as a teacher to the course.\n\n'
           u'You can register here: %s\n\n'
           u'Best regards,\n%s\'s team')
    send_mail(_(u'You have been invited to be a teacher in %s') %
              invitation.course.name,
              _(msg) % (invitation.course.name,
                        invitation.host.get_full_name(),
                        settings.REGISTRY_URL,
                        site.name),
              settings.DEFAULT_FROM_EMAIL,
              [invitation.email])
