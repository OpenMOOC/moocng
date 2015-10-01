# -*- coding: utf-8 -*-

# Copyright 2012 UNED
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
import hashlib
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.sites.models import Site


def validate_png_image(value):
    # The value.file has content_type attr only if you are sending a image
    if hasattr(value.file, 'content_type') and value.file.content_type != 'image/png':
        raise ValidationError(_(u'The image is not a png'))


def build_absolute_url(url):
    current_site = Site.objects.get_current()
    return 'https://%s%s' % (current_site.domain, url)


IDENTITY_CHOICES = (
    ('email', _(u'User email')),
)


class Identity(models.Model):
    user = models.OneToOneField(User, verbose_name=_(u'User identity'),
                                blank=False, null=False,
                                related_name='identity')
    type = models.CharField(verbose_name=_(u'Identity type'),
                            blank=False, null=False, max_length=255,
                            choices=IDENTITY_CHOICES,
                            default=IDENTITY_CHOICES[0][0])
    identity_hash = models.CharField(verbose_name=_(u'Identity hash'),
                                     blank=True, null=False, max_length=255)
    hashed = models.BooleanField(verbose_name=_(u'Hashed'), default=True)
    salt = models.CharField(verbose_name=_(u'Identity salt'),
                            blank=True, null=True, max_length=255)

    class Meta:
        verbose_name = _(u'identity')
        verbose_name_plural = _(u'identities')

    def __unicode__(self):
        return ugettext(u'Identity of {0}').format(self.user.username)

    def to_dict(self):
        return {
            'identity': self.identity_hash,
            'type': self.type,
            'hashed': self.hashed,
            'salt': self.salt
        }


class Badge(models.Model):
    title = models.CharField(verbose_name=_(u'Name'),
                             blank=False, null=False, unique=True,
                             max_length=255,
                             help_text=_(u'Short, descriptive title'))
    description = models.TextField(verbose_name=_('Badge description'),
                                   blank=False, null=False,
                                   help_text=_(u'Longer description of the '
                                               u'badge and its criteria'))
    image = models.ImageField(verbose_name=_(u'Badge image'),
                              blank=False, null=False, upload_to='badges',
                              validators=[validate_png_image],
                              help_text=_(u'Upload an image to represent the '
                                          u'badge, it must be png'))
    criteria = models.URLField(verbose_name=_(u'Criteria'),
                               blank=False, null=False, max_length=255,
                               help_text=_(u'URL of the criteria for earning '
                                           u'the achievement (recomended: '
                                           u'marked up this up with LRMI)'))
    alignments = models.ManyToManyField('Alignment',
                                        verbose_name=_(u'Alignments'),
                                        blank=True, null=True,
                                        related_name=_(u'alignments'))
    tags = models.ManyToManyField('Tag', verbose_name=_(u'Tags'),
                                  blank=True, null=True,
                                  related_name=_(u'tags'))
    slug = models.SlugField(verbose_name=_(u'Badge slug (moocng)'),
                            blank=False, unique=True, null=False,
                            help_text=_(u'Very short name, for use in URLs and links'))
    created = models.DateTimeField(verbose_name=_(u'Creation date and time (moocng)'),
                                   auto_now_add=True, blank=False)
    modified = models.DateTimeField(verbose_name=_(u'Last modification date and time (moocng)'),
                                    auto_now=True, blank=False)

    class Meta:
        ordering = ['-modified', '-created']
        verbose_name = _(u'badge')
        verbose_name_plural = _(u'badges')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return build_absolute_url(reverse('badge', args=[self.slug]))

    def to_dict(self):
        return {
            'name': self.title,
            'description': self.description,
            'image': build_absolute_url(self.image.url),
            'criteria': self.criteria,
            'issuer': build_absolute_url(reverse('issuer')),
            'alignment': [a.to_dict() for a in self.alignments.all()],
            'tags': [t.name for t in self.tags.all()]
        }


class BadgeByCourse(models.Model):
    CRITERIA_TYPE_CHOICES = (
        (0, _(u'Units checkpoint')),
        (1, _(u'Peer review')),
        (2, _(u'Unique unit'))
    )

    title = models.CharField(verbose_name=_(u'Name'),
                             blank=False, null=False, unique=False,
                             max_length=255)

    description = models.TextField(verbose_name=_(u'Description'),
                             blank=False, null=True)

    criteria = models.TextField(verbose_name=_(u'Criteria'),
                               blank=False, null=False)

    criteria_type = models.IntegerField(verbose_name=_(u'Criteria_type'),
                               blank=False, null=False, choices=CRITERIA_TYPE_CHOICES)

    note = models.IntegerField(verbose_name=_(u'Note'),
                               blank=False, null=False)

    color = models.TextField(verbose_name=_('Color'),
                                   blank=False, null=False)

    course = models.ForeignKey('courses.Course', verbose_name=_(u'Course'))

    # New fields
    image = models.ImageField(verbose_name=_(u'Badge image'),
                              blank=True, null=True, upload_to='badges',
                              validators=[validate_png_image],
                              help_text=_(u'Upload an image to represent the '
                                          u'badge, it must be png'))


    @classmethod
    def create(cls, title, description, criteria, criteria_type, note, color, course):
        badgeByCourse = cls(title=title, description=description, criteria=criteria,criteria_type=criteria_type,note=note,color=color,course=course)
        return badgeByCourse

    class Meta:
        verbose_name = _(u'badges_badgebycourse')
        verbose_name_plural = _(u'badges_badgebycourse')

    def __unicode__(self):
        return self.title

    def to_dict(self):
        return {
            'name': self.title,
            'description': self.description,
            'image': build_absolute_url(reverse('badge_image', args=(self.id, ) )),
            'criteria': build_absolute_url('/'+settings.BADGES_CRITERIA_URL),
            'issuer': build_absolute_url(reverse('issuer')),
        }


class Award(models.Model):
    """
    Only available verification type 'hosted' by design decision.
    If 'signed' type is needed, it's necessary to add
    corresponding fields and methods, and refactor in to_dict()
    """
    uuid = models.CharField(verbose_name=_(u'Award uuid'),
                            db_index=True, max_length=255,
                            default=lambda: str(uuid.uuid1()))
    user = models.ForeignKey(User, verbose_name=_(u'Awardee'),
                             blank=False, null=False,
                             related_name='user_awards')
    badge = models.ForeignKey('Badge', verbose_name=_(u'Badge'),
                              blank=False, null=False,
                              related_name='awards_set')
    awarded = models.DateTimeField(verbose_name=_(u'Awarding date and time'),
                                   blank=False, null=False, auto_now_add=True)
    evidence = models.CharField(verbose_name=_(u'URL with assertion evidence'),
                                blank=True, null=True, max_length=255)
    expires = models.DateTimeField(blank=True, null=True,
                                   verbose_name=_(u'When a badge should no longer be '
                                   u'considered valid'))
    modified = models.DateTimeField(verbose_name=_(u'Last modification date and time'),
                                    blank=False, null=False, auto_now=True)
    identity_type = models.CharField(verbose_name=_(u'Identity type'),
                                     blank=True, null=False, max_length=255,
                                     choices=IDENTITY_CHOICES,
                                     default=IDENTITY_CHOICES[0][0])
    identity_hash = models.CharField(verbose_name=_(u'Identity hash'),
                                     blank=True, null=False, max_length=255)
    identity_hashed = models.BooleanField(verbose_name=_(u'Hashed'),
                                          default=True)
    identity_salt = models.CharField(verbose_name=_(u'Identity salt'),
                                     blank=True, null=True, max_length=255)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-modified', '-awarded']
        verbose_name = _(u'award')
        verbose_name_plural = _(u'awards')

    def __unicode__(self):
        return ugettext(u'{0} awarded to {1}').format(self.badge.title, self.user.username)

    @property
    def revoked(self):
        return Revocation.objects.filter(award=self).count() > 0

    def get_image_url(self):
        return "https://{0}/baker?assertion={1}".format(settings.BADGES_SERVICE_URL, self.get_absolute_url())

    def get_image_public_url(self):
        return self.get_image_url()

    def get_absolute_url(self):
        url = reverse('assertion', args=[self.uuid])
        return build_absolute_url(url)

    def to_dict(self):
        return {
            'uid': self.uuid,
            'recipient': {
                'identity': self.identity_hash,
                'type': self.identity_type,
                'hashed': self.identity_hashed,
                'salt': self.identity_salt
            },
            'badge': self.badge.get_absolute_url(),
            'verify': {
                'type': 'hosted',
                'url': self.get_absolute_url()
            },
            'issuedOn': self.awarded.strftime('%Y-%m-%d'),
            'image': self.badge.image and build_absolute_url(self.badge.image.url) or '',
            'evidence': self.evidence,
            'expires': self.expires and self.expires.strftime('%Y-%m-%d') or ''
        }


class Revocation(models.Model):
    award = models.ForeignKey('Award', verbose_name=_(u'Award'), blank=False,
                              null=False, related_name='revocations')
    reason = models.CharField(verbose_name=_(u'Reason for revocation'),
                              blank=False, null=False, max_length=255)

    class Meta:
        verbose_name = _(u'revocation list')
        verbose_name_plural = _(u'revocations list')

    def __unicode__(self):
        return (u'{0} - {1}').format(self.award.uuid, self.reason)

    def to_dict(self):
        return {
            self.award.uuid: self.reason,
        }


class Alignment(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), blank=False, null=False,
                            max_length=255)
    url = models.CharField(verbose_name=_(u'Url'), blank=False, null=False,
                           max_length=255)
    description = models.TextField(verbose_name=_('Description'), blank=True,
                                   null=True)

    class Meta:
        verbose_name = _(u'alignment')
        verbose_name_plural = _('alignments')

    def __unicode__(self):
        return self.name

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description
        }


class Tag(models.Model):
    name = models.CharField(verbose_name=_(u'Tag name'), blank=False,
                            null=False, max_length=255)

    class Meta:
        verbose_name = _(u'tag')
        verbose_name_plural = _(u'tags')

    def __unicode__(self):
        return self.name


def create_identity_for_user(user):
    try:
        user.identity
        current_identity_hash = user.identity.identity_hash
        new_candidate_identity_hash = u'sha256$' + hashlib.sha256(user.email + user.identity.salt).hexdigest()
        if current_identity_hash != new_candidate_identity_hash:
            salt = uuid.uuid4().hex[:5]
            user.identity.salt = salt
            user.identity.identity_hash = u'sha256$' + hashlib.sha256(user.email + salt).hexdigest()
            user.identity.save()
    except:
        salt = uuid.uuid4().hex[:5]
        Identity.objects.create(
            user=user,
            identity_hash=u'sha256$' + hashlib.sha256(user.email + salt).hexdigest(),
            salt=salt
        )


@receiver(post_save, sender=Award, dispatch_uid="award_post_save_identity")
def save_identity_for_user(sender, instance, created, **kwargs):
    """
    Handler for copying current identity into award,
    for future consistency
    """
    if created:
        create_identity_for_user(instance.user)
        instance.identity_hash = instance.user.identity.identity_hash
        instance.identity_type = instance.user.identity.type
        instance.identity_hashed = instance.user.identity.hashed
        instance.identity_salt = instance.user.identity.salt
        instance.save()
