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

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Course


class Invitation(models.Model):

    host = models.ForeignKey(User, verbose_name=_(u'Host'), blank=False,
                             null=False)
    email = models.EmailField(verbose_name=_(u'Email'), blank=False,
                              null=False)
    course = models.ForeignKey(Course, verbose_name=_(u'Course'), blank=False,
                               null=False)
    datetime = models.DateTimeField(verbose_name=_(u'Date and time'),
                                    blank=False, null=False)
