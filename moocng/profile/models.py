# -*- coding: utf-8 -*-
# Copyright 2013 UNED
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

from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Announcement

class Organization(models.Model):
    name = models.CharField(verbose_name=_(u"Organization name"),
                                    max_length=256)
    logo = models.ImageField(upload_to="organizations",
                            # height_field=256,
                            # width_field=256,
                            verbose_name=_(u"Organization logo"),
                            max_length=256)

    def __unicode__(self):
        return unicode(self.name)


class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'))
    last_announcement = models.ForeignKey(Announcement,
                                          verbose_name=_('Last announcement viewed'),
                                          null=True,
                                          blank=True)

    organization = models.ManyToManyField(Organization, verbose_name=_(u'Organization'),
                                                        null=True)
    GENDER_CHOICES = (
        ('m', _(u'Male')),
        ('f', _(u'Female'))
    )
    gender = models.CharField(verbose_name=_(u"Gender"),
                                    max_length=1,
                                    choices=GENDER_CHOICES,
                                    null=True,
                                    blank=True)
    personalweb = models.CharField(verbose_name=_(u"Personal website"),
                                    max_length=256,
                                    null=True,
                                    blank=True)
    birthdate = models.DateField(verbose_name=_(u"Birthdate"),
                                    null=True)
    bio = models.TextField(verbose_name=_(u"Biography"),
                                    null=True,
                                    blank=True)
    karma = models.IntegerField(verbose_name=_(u"Karma"),
                                    default=0)
    

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        return unicode(self.user)

@receiver(signals.post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, **kwargs):
    tables = connection.introspection.table_names()
    try:
        profile = instance.get_profile()
    except UserProfile.DoesNotExist:
        profile = None
    if not profile and UserProfile._meta.db_table in tables:
        UserProfile.objects.create(user=instance)
