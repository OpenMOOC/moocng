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

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals, Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from moocng.assets import cache
from moocng.courses.models import KnowledgeQuantum

from tinymce.models import HTMLField

from datetime import timedelta


class Asset(models.Model):

    slot_duration = models.PositiveSmallIntegerField(verbose_name=_(u'Slot duration'))
    name = models.CharField(verbose_name=_(u'Name'),
                            max_length=200)
    description = HTMLField(verbose_name=_(u'Description'),
                            blank=True, null=False)
    capacity = models.PositiveIntegerField(verbose_name=_(u'Student capacity'))
    max_bookable_slots = models.PositiveSmallIntegerField(verbose_name=_(u'Maximun bookable slots'))
    reservation_in_advance = models.PositiveIntegerField(verbose_name=_(u'Time required in advance for reservation'),
                                                         default=120)
    cancelation_in_advance = models.PositiveIntegerField(verbose_name=_(u'Time required in advance to cancel a reservation'),
                                                         default=120)
    asset_url = models.URLField(verbose_name=_('Asset URL'),
                                blank=True, null=False)

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


from moocng.assets.utils import check_reservations_slot_duration, send_cancellation_email


def assure_granularity(sender, instance, **kwargs):
    difference = instance.slot_duration % settings.ASSET_SLOT_GRANULARITY
    if difference != 0:
        if difference > (settings.ASSET_SLOT_GRANULARITY / 2):
            instance.slot_duration += settings.ASSET_SLOT_GRANULARITY - difference
        else:
            instance.slot_duration -= difference
    if instance.slot_duration == 0:
        instance.slot_duration = settings.ASSET_SLOT_GRANULARITY


def check_duration_reservations(sender, instance, **kwargs):
    check_reservations_slot_duration(instance)


def remove_reservations(sender, instance, **kwargs):
    limit = instance.available_to + timedelta(1, 0)  # The final day is allowed
    assetIds = instance.assets.values_list('id', flat=True)
    affected_reservations = Reservation.objects.filter(reserved_from__id=instance.id)
    affected_reservations = affected_reservations.filter(~Q(asset__id__in=assetIds)
                                                         | Q(reservation_begins__lt=instance.available_from)
                                                         | Q(reservation_ends__gt=limit))
    affected_reservations = affected_reservations.distinct()
    for i in affected_reservations:
        send_cancellation_email(i)
        i.delete()


def remove_reservations_delete(sender, instance, **kwargs):
    affected_reservations = Reservation.objects.filter(reserved_from__id=instance.id)
    for i in affected_reservations:
        send_cancellation_email(i)
        i.delete()


def invalidate_cache(sender, instance, **kwargs):
    try:
        cache.invalidate_course_has_assets_in_cache(instance.kq.unit.course)
    except ObjectDoesNotExist:
        pass


signals.pre_save.connect(assure_granularity, sender=Asset)
signals.post_save.connect(check_duration_reservations, sender=Asset)
signals.post_save.connect(remove_reservations, sender=AssetAvailability)
signals.pre_delete.connect(remove_reservations_delete, sender=AssetAvailability)
signals.post_save.connect(invalidate_cache, sender=AssetAvailability)
signals.post_delete.connect(invalidate_cache, sender=AssetAvailability)
