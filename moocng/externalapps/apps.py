# -*- coding: utf-8 -*-
from django.conf import settings

from moocng.externalapps.base import ExternalApp


class Askbot(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        instance_type = 'askbot'
        instances = settings.MOOCNG_EXTERNALAPPS['askbot']['instances']

class NodeBB(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        instance_type = 'nodebb'
        instances = settings.MOOCNG_EXTERNALAPPS['nodebb']['instances']
