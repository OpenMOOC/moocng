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

# It uses code from https://github.com/lmorchard/django-badger
# Copyright (c) 2011, Mozilla    BSD 3-Clause License

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


def validate_png_image(value):
    if value.file.content_type != 'image/png':
        raise ValidationError(_(u'The image is not a png'))


class Badge(models.Model):
    title = models.CharField(
        max_length=255, blank=False, unique=True,
        verbose_name=_(u'Badge title'), null=False,
        help_text=_(u'Short, descriptive title'))
    slug = models.SlugField(
        blank=False, unique=True, null=False, verbose_name=_(u'Badge slug'),
        help_text=_(u'Very short name, for use in URLs and links'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_(u'Badge description'),
        help_text=_(u'Longer description of the badge and its criteria'))
    image = models.ImageField(
        blank=False, null=False, verbose_name=_(u'Badge image'),
        upload_to='badges', validators=[validate_png_image],
        help_text=_("Upload an image to represent the badge, it must be png"))
    created = models.DateTimeField(
        auto_now_add=True, blank=False,
        verbose_name=_(u'Creation date and time'))
    modified = models.DateTimeField(
        auto_now=True, blank=False,
        verbose_name=_(u'Last modification date and time'))

    class Meta:
        ordering = ['-modified', '-created']
        verbose_name = _(u'badge')
        verbose_name_plural = _(u'badges')

    def __unicode__(self):
        return self.title


class Award(models.Model):
    badge = models.ForeignKey(
        Badge, verbose_name=_(u'Badge'), blank=False, null=False,
        related_name='awards_set')
    user = models.ForeignKey(
        User, verbose_name=_(u'Awardee'), related_name='user_awards',
        blank=False, null=False)
    awarded = models.DateTimeField(
        auto_now_add=True, blank=False, null=False,
        verbose_name=_(u'Awarding date and time'))
    modified = models.DateTimeField(
        auto_now=True, blank=False, null=False,
        verbose_name=_(u'Last modification date and time'))

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-modified', '-awarded']
        verbose_name = _(u'award')
        verbose_name_plural = _(u'awards')

    def __unicode__(self):
        return "%s awarded to %s" % (self.badge.title, self.user.username)

    def get_image_url(self):
        return self.badge.image.url

    def get_image_public_url(self):
        current_site = Site.objects.get_current()
        url = reverse('badge_image', args=[self.badge.slug, self.user.id])
        return 'http://%s%s' % (current_site.domain, url)
