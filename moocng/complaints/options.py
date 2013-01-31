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
from django.utils.translation import ugettext_lazy as _

COMUNICATION_TYPE = (('feedback', _('Feedback / Comment')),
                     ('incidence', _('Incidence')),
                     ('metodology', _('Metodology')),
                     ('certification', _('Certification')),
                     ('platform', _('Platform')),
                     ('registration', _('Registration')),
                     ('rights',_('Rights violation')),
                     ('unsubscribe',_('Remove account')),
                     ('other',_('Other')))


def comunication_options():
    if not getattr(settings, "ENABLED_COMUNICATIONS", None):
        return COMUNICATION_TYPE
    comunications = []
    comunication_type_dict = dict(COMUNICATION_TYPE)

    for communication_key in settings.ENABLED_COMUNICATIONS:
        if communication_key in comunication_type_dict:
            comunications.append((communication_key,
                                  comunication_type_dict[communication_key]))
    return tuple(comunications)


