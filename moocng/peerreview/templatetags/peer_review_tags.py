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


from django import template

from moocng.mongodb import get_db
from moocng.peerreview.utils import course_has_peer_review_assignments
from moocng.peerreview.models import EvaluationCriterion

register = template.Library()


class IfHasPeerReviewAssignmentsNode(template.Node):

    def __init__(self, course, nodelist_true, nodelist_false):
        self.course = template.Variable(course)
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfHasPeerReviewAssignmentsNode>"

    def render(self, context):
        course = self.course.resolve(context)
        if course_has_peer_review_assignments(course):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag
def if_has_peer_review_assignments(parser, token):
    bits = token.contents.split()

    try:
        course = bits[1]
    except IndexError:
        raise template.TemplateSyntaxError('%r tag requires a single argument'
                                           % bits[0])

    nodelist_true = parser.parse(('else', 'endif_has_peer_review_assignments'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_has_peer_review_assignments', ))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return IfHasPeerReviewAssignmentsNode(course, nodelist_true, nodelist_false)


@register.inclusion_tag('peerreview/pending_reviews.html')
def pending_reviews(peer_review_assignment, user, course, user_submissions):
    db = get_db()
    peer_review_reviews = db.get_collection('peer_review_reviews')
    reviewed = peer_review_reviews.find({
        'reviewer': user.id,
        'kq': peer_review_assignment.kq.id,
    })
    peer_review_submissions = db.get_collection('peer_review_submissions')
    assigned = peer_review_submissions.find({
        'assigned_to': user.id,
        'kq': peer_review_assignment.kq.id,
    })
    pending = peer_review_assignment.minimum_reviewers - reviewed.count()
    has_sent_submission = peer_review_assignment.id in user_submissions
    return {
        'reviewed': reviewed,
        'assigned': assigned,
        'pending': pending,
        'has_sent_submission': has_sent_submission,
        'peer_review_assignment_id': peer_review_assignment.id,
        'course_slug': course.slug
    }


@register.filter
def get_criterion_description(criterion_id):
    try:
        criterion = EvaluationCriterion.objects.get(id=criterion_id)
        return criterion.description
    except EvaluationCriterion.DoesNotExist:
        return ''

@register.filter
def get_criterion_score_descriptions(criterion_id):
    try:
        criterion = EvaluationCriterion.objects.get(id=criterion_id)
        score_descriptions = []
        if criterion.description_score_1:
            score_descriptions.append(criterion.description_score_1)
            score_descriptions.append(criterion.description_score_2)
            score_descriptions.append(criterion.description_score_3)
            score_descriptions.append(criterion.description_score_4)
            score_descriptions.append(criterion.description_score_5)
        return score_descriptions
    except EvaluationCriterion.DoesNotExist:
        return ''

@register.filter
def get_criterion_title(criterion_id):
    try:
        criterion = EvaluationCriterion.objects.get(id=criterion_id)
        return criterion.title
    except EvaluationCriterion.DoesNotExist:
        return ''

