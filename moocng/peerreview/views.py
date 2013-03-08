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

import pymongo

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.forms.formsets import formset_factory
from django.db import IntegrityError

from moocng.api.mongodb import get_db
from moocng.courses.models import Course
from moocng.peerreview.models import PeerReviewAssignment
from moocng.peerreview.utils import course_get_peer_review_assignments, save_review
from moocng.peerreview.forms import ReviewSubmissionForm, EvalutionCriteriaResponseForm
from moocng.teacheradmin.utils import send_mail_wrapper


@require_POST
@login_required
def course_review_assign(request, course_slug, review_id):
    course = get_object_or_404(Course, slug=course_slug)
    review = get_object_or_404(PeerReviewAssignment, id=review_id)
    user_id = request.user.id

    if review.kq.unit.course != course:
        messages.error(request, _('The selected peer review assignment is not part of this course.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    collection = get_db().get_collection('peer_review_submissions')

    submission = collection.find({
        'kq': review.kq.id,
        'assigned_to': user_id
    })
    if submission.count() > 0:
        messages.error(request, _('You already have a submission assigned.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    submission = collection.find({
        'kq': review.kq.id,
        'assigned_to': {
            '$exists': False
        },
        'author': {
            '$ne': user_id
        },
        'reviewers': {
            '$ne': user_id
        }
    }).sort([
        ('reviews', pymongo.ASCENDING),
        ('author_reviews', pymongo.DESCENDING),
    ]).limit(1)

    if submission.count() == 0:
        messages.error(request, _('There is no submission avaliable for you at this moment. Please, try again later.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
    else:
        collection.update({'_id': submission[0]['_id']}, {'$set': {'assigned_to': user_id}})
        return HttpResponseRedirect(reverse('course_review_submission', args=[course_slug, review_id]))


@login_required
def course_reviews(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    assignments = course_get_peer_review_assignments(course)

    return render_to_response('peerreview/reviews.html', {
            'course': course,
            'assignments': assignments,
            }, context_instance=RequestContext(request))


@login_required
def course_review_submission(request, course_slug, review_id):
    course = get_object_or_404(Course, slug=course_slug)
    review = get_object_or_404(PeerReviewAssignment, id=review_id)
    user_id = request.user.id

    if review.kq.unit.course != course:
        messages.error(request, _('The selected peer review assignment is not part of this course.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    collection = get_db().get_collection('peer_review_submissions')

    submission = collection.find({
        'kq': review.kq.id,
        'assigned_to': user_id
    })

    if submission.count() == 0:
        messages.error(request, _('You don\'t have this submission assigned.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    submitter = User.objects.get(id=int(submission[0]['author']))

    criteria_initial = [{'evaluation_criterion_id': criterion.id} for criterion in review.criteria.all()]
    EvalutionCriteriaResponseFormSet = formset_factory(EvalutionCriteriaResponseForm, extra=0, max_num=len(criteria_initial))

    if request.method == "POST":
        submission_form = ReviewSubmissionForm(request.POST)
        criteria_formset = EvalutionCriteriaResponseFormSet(request.POST, initial=criteria_initial)
        if criteria_formset.is_valid() and submission_form.is_valid():
            criteria_values = [int(form.cleaned_data['value']) for form in criteria_formset]
            try:
                save_review(review.kq, request.user, submitter, criteria_values, submission_form.cleaned_data['comments'])
                send_mail_to_submission_owner(review, submission)
            except IntegrityError:
                messages.error(request, _('Your can\'t submit two times the same review.'))
                return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

            messages.success(request, _('Your review has been submitted.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
    else:
        submission_form = ReviewSubmissionForm()
        criteria_formset = EvalutionCriteriaResponseFormSet(initial=criteria_initial)

    return render_to_response('peerreview/review_submission.html', {
            'submission': submission[0],
            'submission_form': submission_form,
            'criteria_formset': criteria_formset,
            'course': course,
            'review': review,
            }, context_instance=RequestContext(request))

def send_mail_to_submission_owner(review, submission):
    subject = _(u'Your assignment "%(nugget)s" has been reviewed') % {'nugget': review.kq.title}
    message = _(u""""Congratulations %(user)s

        The exercise you sent on %(date)s belonging the nugget "%(nugget)s has been reviewed by a classmate.

        Evaluation criteria:

        """) % {
            'user': submission[0]['author'],
            'date': submission[0]['created'],
            'nugget': review.kq.title
        }

    for criterion in review.criteria.all():
        message += _(u"""- %s
            """) % criterion.description

    message += _(u"""
        Your classmate's comment:

        %(comment)s

        Best regards and thank you for learning with Undecoma.es

        %(site)s's team""") % {
            'comment': submission[0]['comment'],
            'site': get_current_site(request).name,
    }
    send_mail_wrapper(subject, message, [submission[0]['author'].email])

