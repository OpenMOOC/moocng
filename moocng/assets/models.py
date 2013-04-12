# Copyright 2013 Rooter Analysis S.L.
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
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from moocng.assets import cache
from moocng.courses.models import KnowledgeQuantum

from tinymce.models import HTMLField


class Asset(models.Model):

    slot_duration = models.PositiveSmallIntegerField(verbose_name=_(u'Slot duration'))
    name = models.CharField(verbose_name=_(u'Name'),
                            max_length=200)
    description = HTMLField(verbose_name=_(u'Description'),
                            blank=True, null=False)
    capacity = models.PositiveIntegerField(verbose_name=_(u'Student capacity'))
    max_bookable_slots = models.PositiveSmallIntegerField(verbose_name=_(u'Maximun bookable slots'))

    class Meta:
        verbose_name = _(u'asset')
        verbose_name_plural = _(u'assets')

    def __unicode__(self):
        return self.name


class AssetAvailability(models.Model):

    kq = models.OneToOneField(KnowledgeQuantum,
                              verbose_name=_(u'KnowledgeQuantum'),
                              related_name='asset_availability')
    assets = models.ManyToManyField(Asset, verbose_name=_(u'Assets'),
                                    related_name='available_in')
    available_from = models.DateField(verbose_name=_(u'Available from'),
                                      blank=True, null=True)
    available_to = models.DateField(verbose_name=_(u'Available to'),
                                    blank=True, null=True)

    class Meta:
        verbose_name = _(u'asset availability')
        verbose_name_plural = _(u'asset availabilities')

    def __unicode__(self):
        return ugettext(u'Assets availables for {0}').format(self.kq)


def invalidate_cache(sender, instance, **kwargs):
    try:
        cache.invalidate_course_has_assets_in_cache(instance.kq.unit.course)
    except ObjectDoesNotExist:
        pass


signals.post_save.connect(invalidate_cache, sender=AssetAvailability)
signals.post_delete.connect(invalidate_cache, sender=AssetAvailability)


class Reservation(models.Model):

    user = models.ForeignKey(User, verbose_name=_(u'User'),
                             null=True, blank=True)
    reserved_from = models.ForeignKey(AssetAvailability,
                                      verbose_name=_(u'Reserved from'),
                                      null=True, blank=True)
    asset = models.ForeignKey(Asset, verbose_name=_(u'Asset'),
                              null=False)
    slot_id = models.PositiveSmallIntegerField(null=True)
    reservation_begins = models.DateTimeField(verbose_name=_(u'Datetime'),
                                              null=False, blank=False)
    reservation_ends = models.DateTimeField(verbose_name=_(u'Datetime'),
                                            null=False, blank=False)

    class Meta:
        verbose_name = _(u'reservation')
        verbose_name_plural = _(u'reservations')

    def __unicode__(self):
        return ugettext(u'Reservation of {0}, made by {1}').format(self.asset, self.user)

