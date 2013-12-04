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

from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from moocng.courses.models import Course, Announcement


class BaseAnnouncementFeed(Feed):

    def title(self, obj):
        return _("Announcements of the %(title)s") % {"title": obj.name}

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.datetime


class AnnouncementCourseFeed(BaseAnnouncementFeed):

    """
    Default RSS feed for the course announcements.

    :returns: RSS Feed

    .. versionadded:: 0.1
    """
    def link(self, obj):
        return obj.get_absolute_url()

    def get_object(self, request, course_slug):
        return get_object_or_404(Course, slug=course_slug)

    def description(self, obj):
        return _('Announcements of the online course "%(course_title)s" on the platform "%(site_name)s".') % {
            "course_title": obj.name,
            "site_name": Site.objects.get_current().name}

    def items(self, obj):
        return Announcement.objects.filter(course=obj).order_by('-datetime')


class AnnouncementPortalFeed(BaseAnnouncementFeed):

    """
    Default RSS feed for the course announcements.

    :returns: RSS Feed

    .. versionadded:: 0.1
    """

    def link(self, obj):
        return '/'

    def get_object(self, request):
        return Site.objects.get_current()

    def description(self, obj):
        return _('Announcements of the "%(site_name)s".') % {"site_name": Site.objects.get_current().name}

    def items(self, obj):
        return Announcement.objects.portal().order_by('-datetime')
