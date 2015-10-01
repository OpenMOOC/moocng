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


from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from adminsortable.models import Sortable
from tinymce.models import HTMLField

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db
from moocng.peerreview import cache
from moocng.peerreview.managers import EvaluationCriterionManager, PeerReviewAssignmentManager


class PeerReviewAssignment(models.Model):
    description = HTMLField(verbose_name=_(u'Description'),
                            blank=True, null=False)
    minimum_reviewers = models.PositiveSmallIntegerField(verbose_name=_(u'Minimum reviewers'))
    kq = models.OneToOneField(KnowledgeQuantum, verbose_name=_(u'Nugget'),
                              blank=False, null=False)
    objects = PeerReviewAssignmentManager()

    class Meta:
        verbose_name = _(u'peer review assignment')
        verbose_name_plural = _(u'peer review assignments')

    def is_completed(self, user, visited=None):

        db = get_db()

        if visited is None:
            visited = self.kq.kq_visited_by(user)
            if not visited:
                return False

        # Verify if user has sent a submission
        submissions = db.get_collection("peer_review_submissions")
        user_submission = submissions.find_one({
            "kq": self.kq.id,
            "author": user.id
        })

        if not user_submission:
            return False

        if user_submission.get("author_reviews", 0) < self.minimum_reviewers:
            return False

        return True

    def natural_key(self):
        return self.kq.natural_key()

    def __unicode__(self):
        return unicode(self.kq)


def invalidate_cache(sender, instance, **kwargs):
    try:
        course = instance.kq.unit.course
        cache.invalidate_course_has_peer_review_assignment_in_cache(course)
    except ObjectDoesNotExist:  # The knowledge quantum is being deleted
        pass


signals.post_save.connect(invalidate_cache, sender=PeerReviewAssignment)
signals.post_delete.connect(invalidate_cache, sender=PeerReviewAssignment)


class EvaluationCriterion(Sortable):
    assignment = models.ForeignKey(PeerReviewAssignment,
                                   verbose_name=_(u'Peer review assignment'),
                                   related_name='criteria')
    title = models.CharField(verbose_name=_(u'Title'), max_length=100,
                             blank=False, null=False)
    description = models.TextField(verbose_name=_(u'Description'),
                                   blank=True, null=False)
    description_score_1 = models.TextField(verbose_name=_(u'Description for score 1'),
                                        blank=True, null=False)
    description_score_2 = models.TextField(verbose_name=_(u'Description for score 2'),
                                        blank=True, null=False)
    description_score_3 = models.TextField(verbose_name=_(u'Description for score 3'),
                                        blank=True, null=False)
    description_score_4 = models.TextField(verbose_name=_(u'Description for score 4'),
                                        blank=True, null=False)
    description_score_5 = models.TextField(verbose_name=_(u'Description for score 5'),
                                        blank=True, null=False)
    objects = EvaluationCriterionManager()

    class Meta(Sortable.Meta):
        verbose_name = _(u'evaluation criterion')
        verbose_name_plural = _(u'evaluation criteria')
        unique_together = ('title', 'assignment')

    def natural_key(self):
        return self.assignment.natural_key() + (self.title, )

    def __unicode__(self):
        return ugettext(u'{0} - EvaluationCriterion {1}').format(self.assignment.kq, self.title)
