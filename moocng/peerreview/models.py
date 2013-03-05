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
from django.utils.translation import ugettext_lazy as _

from adminsortable.models import Sortable
from tinymce.models import HTMLField

from moocng.courses.models import KnowledgeQuantum


class PeerReviewAssignment(models.Model):
    description = HTMLField(verbose_name=_(u'Description'),
                            blank=True, null=False)
    minimum_reviewers = models.PositiveSmallIntegerField()
    knowledge_quantum = models.ForeignKey(KnowledgeQuantum,
                                          verbose_name=_(u'Knowledge quantum'),
                                          blank=False, null=False)

    class Meta:
        verbose_name = _(u'peer review assignment')
        verbose_name_plural = _(u'peer review assignments')


class EvaluationCriterion(Sortable):
    assignment = models.ForeignKey(PeerReviewAssignment,
                                   verbose_name=_(u'Peer review assignment'))
    description = models.TextField(verbose_name=_(u'Description'),
                                   blank=True, null=False)

    class Meta(Sortable.Meta):
        verbose_name = _(u'evaluation criterion')
        verbose_name_plural = _(u'evaluation criteria')
