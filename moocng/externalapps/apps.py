# -*- coding: utf-8 -*-
from django.conf import settings

from moocng.externalapps.base import ExternalApp


class Askbot(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        instance_type = 'askbot'
        instances = settings.MOOCNG_EXTERNALAPPS['askbot']['instances']


class Wordpress(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        instance_type = 'wordpress'
        instances = settings.MOOCNG_EXTERNALAPPS['wordpress']['instances']


class Wiki(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        instance_type = 'wiki'
        instances = settings.MOOCNG_EXTERNALAPPS['wiki']['instances']
