# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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
    context = {
        'theme': {
            'logo': settings.STATIC_URL + u'img/logo.png',
            'subtitle': u'Knowledge for the masses',
            'top_banner': settings.STATIC_URL + u'img/top_banner.jpg',
            'right_banner1': settings.STATIC_URL + u'img/right_banner1.jpg',
            'right_banner2': settings.STATIC_URL + u'img/right_banner2.jpg',
            'bootstrap_css': settings.STATIC_URL + u'css/bootstrap.min.css',
            'moocng_css': settings.STATIC_URL + u'css/moocng.css',
            'cert_banner': settings.STATIC_URL + u'img/cert_banner.png',
        }
    }

    try:
        context['theme'].update(settings.MOOCNG_THEME)
    except AttributeError:
        pass

    try:
        context['show_tos'] = settings.SHOW_TOS
    except AttributeError:
        context['show_tos'] = True

    return context


def google_analytics(request):
    context = {}

    try:
        context['google_analytics'] = settings.GOOGLE_ANALYTICS_CODE
    except AttributeError:
        context['google_analytics'] = ''

    return context


def certificate_url(request):
    context = {}
    try:
        context['certificate_provider_url'] = settings.CERTIFICATE_URL
    except AttributeError:
        context['certificate_provider_url'] = '#'

    return context


def extra_settings(request):

    try:
        sandbox = settings.ALLOW_PUBLIC_COURSE_CREATION
    except AttributeError:
        sandbox = ''

    try:
        mathjax_enabled = settings.MATHJAX_ENABLED
    except AttributeError:
        mathjax_enabled = False

    context = {
        'sandbox': sandbox,
        'mathjax_enabled': mathjax_enabled,
    }
    return context
