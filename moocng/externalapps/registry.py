# -*- coding: utf-8 -*-
import logging
from pkg_resources import iter_entry_points

from django.conf import settings

logger = logging.getLogger("moocng.externalapps.registry")


class ExternalAppRegistry(dict):

    def __init__(self, *args, **kwargs):
        allowed_moocng_plugins = settings.MOOCNG_EXTERNALAPPS
        for entry_point in iter_entry_points(group='moocng.externalapp', name=None):
            if entry_point.name in allowed_moocng_plugins:
                if entry_point.name in self:
                    logger.warn("Duplicate entry point: %s" % entry_point.name)
                else:
                    logger.debug("Registering entry point: %s" % entry_point.name)
                    self[entry_point.name] = entry_point.load()
            else:
                logger.warn("Entry point '%s' not registered. Please, check setting 'MOOCNG_EXTERNALAPPS' in your 'settings.py'" % entry_point.name)
        super(ExternalAppRegistry, self).__init__(*args, **kwargs)

    def get_app_by_name(self, name):
       return self.get(name, None)

    def all(self):
        return self.keys()
