# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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
import datetime

from django.db import models
from django.db.models.query import QuerySet


class MassiveEmailQuerySet(QuerySet):

    def recents(self):
        now = datetime.datetime.now()
        first_day = datetime.date(day=1, month=now.month, year=now.year)
        return self.filter(datetime__gte=first_day, datetime__lte=now)


class MassiveEmailManager(models.Manager):

    """
    Manager function for mass amil sending when the teacher creates an announcement
    in the course.

    .. versionadded:: 0.1
    """

    def get_query_set(self):
        return MassiveEmailQuerySet(self.model, using=self._db)

    def create_from_announcement(self, announcement, massive_email_type='course'):
        return super(MassiveEmailManager, self).create(
            course=announcement.course,
            datetime=announcement.datetime,
            subject=announcement.title,
            message=announcement.content,
            massive_email_type=massive_email_type,
        )

    def recents(self):
        return self.get_query_set().recents()
