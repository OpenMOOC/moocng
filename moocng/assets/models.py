# Copyright (c) 2013 Grupo Opentia
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

    kq = models.ForeignKey(KnowledgeQuantum,
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


def invalidate_cache(sender, **kwargs):
    #TODO
    return None
    #if kwargs['action'] not in ('post_add', 'post_remove', 'post_clear'):
        #return

    #kqs = []
    #if kwargs['reverse']:
        #kqs.append(instance)
    #elif kwargs['pk_set'] is not None:
        #kqs = KnowledgeQuantum.objects.filter(id__in=kwargs['pk_set'])

    #for i in kqs:
        #course = i.unit.course
        #cache.invalidate_course_has_assets_in_cache(course)


signals.m2m_changed.connect(invalidate_cache, sender=Asset.available_in)
signals.m2m_changed.connect(invalidate_cache, sender=AssetAvailability.assets)


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
