from django.contrib.sites.models import Site, RequestSite
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def site(request):
    """Sets in the present context information about the current site."""

    # Current SiteManager already handles prevention of spurious
    # database calls. If the user does not have the Sites framework
    # installed, a RequestSite object is an appropriate fallback.
    try:
        models.get_app('sites')
        site_obj = Site.objects.get_current()
    except ImproperlyConfigured:
        site_obj = RequestSite(request)
    return {'site': site_obj}


def theme(request):
    theme = {
        'theme': {
            'subtitle': u'Knowledge for the masses',
            'top_banner': u'top_banner.jpg',
            'right_banner': u'right_banner.jpg',
            }
        }

    try:
        theme['theme'].update(settings.MOOCNG_THEME)
    except AttributeError:
        pass

    return theme
