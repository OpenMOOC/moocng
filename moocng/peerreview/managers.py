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

from django.db import models
from django.db.models import Q


class PeerReviewAssignmentManager(models.Manager):

    def from_course(self, course):
        return self.get_query_set().filter(
            kq__unit__course=course).order_by('kq__unit__order', 'kq__order')

    def visible_from_course(self, user, course):
        if user.is_superuser or user.is_staff:
            return self.from_course(course)
        elif user.is_anonymous():
            return []
        else:
            return self.from_course(course).filter(
                Q(kq__unit__status='p') |
                Q(kq__unit__status='l', kq__unit__course__courseteacher__teacher=user, kq__unit__course__courseteacher__course=course) |
                Q(kq__unit__status='d', kq__unit__course__courseteacher__teacher=user, kq__unit__course__courseteacher__course=course)).distinct()

    def get_by_natural_key(self, course_slug, unit_title, kq_title):
        return self.get(kq__title=kq_title, kq__unit__title=unit_title, kq__unit__course__slug=course_slug)


class EvaluationCriterionManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, kq_title, title):
        return self.get(assignment__kq__title=kq_title,
                        assignment__kq__unit__title=unit_title,
                        assignment__kq__unit__course__slug=course_slug,
                        title=title)
