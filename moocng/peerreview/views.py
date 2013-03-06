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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from moocng.api.mongodb import get_db
from moocng.courses.models import Course
from moocng.peerreview.models import PeerReviewAssignment
from moocng.peerreview.utils import course_get_peer_review_assignments


@require_POST
@login_required
def course_review_assign(request, course_slug, review_id):
    course = get_object_or_404(Course, slug=course_slug)
    review = get_object_or_404(PeerReviewAssignment, id=review_id)
    user_id = request.user.id

    if review.knowledge_quantum.unit.course != course:
        messages.error(request, _('The selected peer review assignment is not part of this course.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    collection = get_db().get_collection('peer_review_submissions')

    submission = collection.find({
        'kq': review.knowledge_quantum.id,
        'assigned_to': user_id
    })
    if submission.count() > 0:
        messages.error(request, _('You already have a submission assigned.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    submission = collection.find({
        'kq': review.knowledge_quantum.id,
        'assigned_to': {
            '$exists': False
        },
        'author': {
            '$ne': user_id
        }
    }).sort('reviews').limit(1)
    if submission.count() == 0:
        messages.error(request, _('There is no submission avaliable for you at this moment. Please, try again later.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
    else:
        collection.update({'_id': submission[0]['_id']}, {'$set': {'assigned_to': user_id}})
        #TODO: Redirect to review submission view
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))


@login_required
def course_reviews(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    assignments = course_get_peer_review_assignments(course)

    return render_to_response('peerreview/reviews.html', {
            'course': course,
            'assignments': assignments,
            }, context_instance=RequestContext(request))
