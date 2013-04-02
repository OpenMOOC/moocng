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
from django.utils.translation import ugettext_lazy as _

from tinymce.models import HTMLField

class Asset(models.Model):

    slot_duration = models.PositiveSmallIntegerField(verbose_name=_(u'Slot duration'))
    name = models.CharField(verbose_name=_(u'Name'), max_length = 200)
    description = HTMLField(verbose_name=_(u'Description'), blank = True, null = False)
    capacity = models.PositiveIntegerField(verbose_name=_(u'Student capacity'))
    max_bookable_slots = models.PositiveSmallIntegerField(verbose_name=_(u'Maximun bookable slots'))

    class Meta:
        verbose_name = _(u'asset')
        verbose_name_plural = _(u'assets')
