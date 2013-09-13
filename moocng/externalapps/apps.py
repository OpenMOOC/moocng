# -*- coding: utf-8 -*-
from django.conf import settings

from moocng.externalapps.base import ExternalApp


class Askbot(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        app_name = 'askbot'
        description = 'askbot description'
        instances = settings.MOOCNG_EXTERNALAPPS['askbot']['instances']


class Wordpress(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        app_name = 'wordpress'
        description = 'wordpress description'
        instances = settings.MOOCNG_EXTERNALAPPS['wordpress']['instances']


class Wiki(ExternalApp):

    class Meta:
        model = 'externalapps.ExternalApp'
        app_name = 'wiki'
        description = 'wiki description'
        instances = settings.MOOCNG_EXTERNALAPPS['wiki']['instances']
