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
import datetime
import hashlib
import random

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from moocng.badges.utils import get_openbadge_keys
from jwt import generate_jwt


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

    def as_json(self):
        current_site = Site.objects.get_current()
        criteria_url = self.course.get().get_absolute_url() if self.course else ''
        criteria_full_url = 'http://%s%s' % (current_site.domain, criteria_url)
        issuer_url = reverse('openbadge_issuer')
        issuer_full_url = 'http://%s%s' % (current_site.domain, issuer_url)
        badge_class_json = {
          "name": self.title,
          "description": self.description,
          "image": 'http://%s%s' % (current_site.domain, self.image.url) ,
          "criteria": criteria_full_url,
          "issuer": issuer_full_url,
          "alignment": []
        }
        return badge_class_json


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
        return ugettext(u'{0} awarded to {1}').format(self.badge.title, self.user.username)

    def get_image_url(self):
        return self.badge.image.url

    def get_image_public_url(self):
        current_site = Site.objects.get_current()
        url = reverse('badge_image_email', args=[self.badge.slug, self.user.email])
        return 'http://%s%s' % (current_site.domain, url)


class BadgeAssertion(models.Model):

    award = models.ForeignKey(
        Award,
        blank=False,
        null=False,
        verbose_name=_(u'Award'))

    user = models.ForeignKey(
        User,
        blank=False,
        null=False,
        verbose_name=_(u'Awardee'))

    class Meta:
        unique_together = ('user', 'award')

    def assertion_url(self):
        current_site = Site.objects.get_current()
        url = reverse('openbadge_assertion', args=[self.award.badge.slug])
        return 'http://%s%s' % (current_site.domain, url)

    def get_recipient_json(self):
        salt, hashed_msg = self.hash_msg(self.user.email)
        recipient = {
              "type": "email",
              "hashed": True,
              "salt": salt,
              "identity": hashed_msg
        }
        return recipient

    def hash_msg(self, msg):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:7]
        hashed_msg = 'sha256$' + hashlib.sha256(msg + salt).hexdigest()
        return (salt, hashed_msg)

    def as_json_web_signature(self):
        openbadge_keys = get_openbadge_keys()
        current_site = Site.objects.get_current()
        payload = {
            "uid": self.award.badge.__hash__(),
            "recipient": self.get_recipient_json(),
            "image": 'http://%s%s' % (current_site.domain, self.award.get_image_url()),
            "issuedOn": self.award.awarded.isoformat(),
            "badge": self.award.badge.as_json(),
            "verify": {
                "type": "signed",
                "url": 'http://%s%s' % (current_site.domain, reverse('openbadge_public_key'))
            }
        }
        token = generate_jwt(payload, openbadge_keys['priv_key'], 'RS256', datetime.timedelta(minutes=10))
        return token
