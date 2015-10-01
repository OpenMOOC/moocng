# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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
from django.utils.translation import ugettext as _


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
            'logo_big': settings.STATIC_URL + u'img/logo_big.png',
            'logo_mini': settings.STATIC_URL + u'img/logo_mini.png',
            'subtitle': u'Knowledge for the masses',
            'top_banner': settings.STATIC_URL + u'img/top_banner.jpg',
            'top_banner_title': u'<strong>OpenMOOC</strong>',
            'top_banner_subtitle': u'A platform created to facilitate the search for open educational resources',
            'bootstrap_css': settings.STATIC_URL + u'css/bootstrap.min.css',
            'moocng_css': settings.STATIC_URL + u'css/moocng.css',
            'favicon_dir': settings.STATIC_URL + u'img/favicon/',
            'course_default_thumbnail': settings.STATIC_URL + u'img/classroom.png',
            'course_overview_default_background': settings.STATIC_URL + u'img/course_bck.jpg',
            'link_home': u'/',
            'link_catalogue': u'/#catalogue',
            'link_tos': u'/tos',
            'link_privacy': u'/legal',
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
        site_url = settings.SITE_URL
    except AttributeError:
        site_url = ''

    try:
        sandbox = settings.ALLOW_PUBLIC_COURSE_CREATION
    except AttributeError:
        sandbox = ''

    try:
        mathjax_enabled = settings.MATHJAX_ENABLED
    except AttributeError:
        mathjax_enabled = False

    try:
        feature_teams = settings.FEATURE_TEAMS
    except AttributeError:
        feature_teams = False

    try:
        feature_calendar = settings.FEATURE_CALENDAR
    except AttributeError:
        feature_calendar = False

    try:
        feature_wiki = settings.FEATURE_WIKI
    except AttributeError:
        feature_wiki = False

    try:
        feature_groups = settings.FEATURE_GROUPS
    except AttributeError:
        feature_groups = False

    try:
        feature_groups_video = settings.FEATURE_GROUPS_VIDEO
    except AttributeError:
        feature_groups_video = False

    try:
        feature_forum = settings.FEATURE_FORUM
    except AttributeError:
        feature_forum = False

    try:
        feature_blog = settings.FEATURE_BLOG
    except AttributeError:
        feature_blog = False

    try:
        feature_notifications = settings.FEATURE_NOTIFICATIONS
    except AttributeError:
        feature_notifications = False

    try:
        feature_sec_catalogue = settings.FEATURE_SEC_CATALOGUE
    except AttributeError:
        feature_sec_catalogue = False

    try:
        feature_sec_about = settings.FEATURE_SEC_ABOUT
    except AttributeError:
        feature_sec_about = False

    try:
        feature_sec_howitworks = settings.FEATURE_SEC_HOWITWORKS
    except AttributeError:
        feature_sec_howitworks = False

    try:
        feature_sec_staff = settings.FEATURE_SEC_STAFF
    except AttributeError:
        feature_sec_staff = False

    try:
        feature_sec_faq = settings.FEATURE_SEC_FAQ
    except AttributeError:
        feature_sec_faq = False

    try:
        feature_sec_contact = settings.FEATURE_SEC_CONTACT
    except AttributeError:
        feature_sec_contact = False

    try:
        feature_sec_teachers = settings.FEATURE_SEC_TEACHERS
    except AttributeError:
        feature_sec_teachers = False

    try:
        feature_social = settings.FEATURE_SOCIAL
    except AttributeError:
        feature_social = False

    try:
        feature_ects = settings.FEATURE_ECTS
    except AttributeError:
        feature_ects = False

    try:
        forum_url = settings.FORUM_URL
    except AttributeError:
        forum_url = '#'

    try:
        forum_category_url = settings.FORUM_CATEGORY_URL
    except AttributeError:
        forum_category_url = '#'

    try:
        max_file_size = settings.ATTACHMENTS_MAX_SIZE
    except AttributeError:
        max_file_size = 5

    try:
        profile_provider_url = settings.PROFILE_SERVICE_URL
    except AttributeError:
        profile_provider_url = None

    try:
        feature_geolocation = settings.FEATURE_GEOLOCATION
    except AttributeError:
        feature_geolocation = '#'

    try:
        show_email = settings.SHOW_EMAIL
    except AttributeError:
        show_email = False

    try:
        show_username = settings.SHOW_USERNAME
    except AttributeError:
        show_username = False

    try:
        show_logout = settings.SHOW_LOGOUT
    except AttributeError:
        show_logout = False

    context = {
        'site_url': site_url,
        'sandbox': sandbox,
        'mathjax_enabled': mathjax_enabled,
        'feature_teams': feature_teams,
        'feature_calendar': feature_calendar,
        'feature_wiki': feature_wiki,
        'feature_groups': feature_groups,
        'feature_groups_video': feature_groups_video,
        'feature_forum': feature_forum,
        'feature_blog': feature_blog,
        'feature_notifications': feature_notifications,
        'feature_sec_catalogue': feature_sec_catalogue,
        'feature_sec_about': feature_sec_about,
        'feature_sec_howitworks': feature_sec_howitworks,
        'feature_sec_staff': feature_sec_staff,
        'feature_sec_faq': feature_sec_faq,
        'feature_sec_contact': feature_sec_contact,
        'feature_sec_teachers': feature_sec_teachers,
        'feature_social': feature_social,
        'feature_ects': feature_ects,
        'forum_url': forum_url,
        'forum_category_url': forum_category_url,
        'max_file_size': max_file_size,
        'profile_provider_url': profile_provider_url,
        'feature_geolocation': feature_geolocation,
        'show_username': show_username,
        'show_email': show_email,
        'show_logout': show_logout,
    }

    return context


def num_announcement_dont_viewed(request):
    user = request.user
    if user.is_anonymous():
        return {'profile': None,
                'announcements_dont_viewed': 0}
    profile = user.get_profile()
    from moocng.courses.models import Announcement
    announcement_dont_viewed = Announcement.objects.portal()
    last_announcement_viewed = getattr(profile, 'last_announcement', None)
    if last_announcement_viewed:
        announcement_dont_viewed = announcement_dont_viewed.filter(datetime__gt=last_announcement_viewed.datetime)
    return {'profile': profile,
            'announcements_dont_viewed': announcement_dont_viewed.count()}
