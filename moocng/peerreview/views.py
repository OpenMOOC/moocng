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

from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import urllib
import time

import boto
import pymongo

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from moocng.api.mongodb import get_db
from moocng.courses.models import Course, KnowledgeQuantum
from moocng.courses.utils import send_mail_wrapper
from moocng.peerreview.forms import ReviewSubmissionForm, EvalutionCriteriaResponseForm
from moocng.peerreview.models import PeerReviewAssignment, EvaluationCriterion
from moocng.peerreview.utils import course_get_peer_review_assignments, save_review


@login_required
def course_review_assign(request, course_slug, assignment_id):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(PeerReviewAssignment, id=assignment_id)
    user_id = request.user.id

    if assignment.kq.unit.course != course:
        messages.error(request, _('The selected peer review assignment is not part of this course.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    collection = get_db().get_collection('peer_review_submissions')

    submission = collection.find({
        'kq': assignment.kq.id,
        'assigned_to': user_id
    })
    if submission.count() > 0:
        messages.error(request, _('You already have a submission assigned.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    max_hours_assigned = timedelta(hours=getattr(settings,
                                   "PEER_REVIEW_ASSIGNATION_EXPIRE", 24))

    assignation_expire = datetime.utcnow() - max_hours_assigned

    submission = collection.find({
        'kq': assignment.kq.id,
        '$or': [
            {
                'assigned_to': {
                    '$exists': False
                },
            },
            {
                'assigned_when': {
                    '$lt': assignation_expire
                },
            }
        ],
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
        collection.update({
            '_id': submission[0]['_id']
        }, {
            '$set': {
                'assigned_to': user_id,
                'assigned_when': datetime.utcnow()
            }
        })
        return HttpResponseRedirect(reverse('course_review_review', args=[course_slug, assignment_id]))


@login_required
def course_reviews(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    assignments = course_get_peer_review_assignments(course)

    collection = get_db().get_collection('peer_review_submissions')
    submissions = collection.find({
            'author': request.user.id,
            'course': course.id,
            }, {'kq': True, '_id': False})
    submissions = [s['kq'] for s in submissions]

    user_submissions = [a.id for a in assignments if a.kq.id in submissions]

    return render_to_response('peerreview/reviews.html', {
            'course': course,
            'assignments': assignments,
            'user_submissions': user_submissions,
            }, context_instance=RequestContext(request))


@login_required
def course_review_review(request, course_slug, assignment_id):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(PeerReviewAssignment, id=assignment_id)
    user_id = request.user.id

    if assignment.kq.unit.course != course:
        messages.error(request, _('The selected peer review assignment is not part of this course.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    collection = get_db().get_collection('peer_review_submissions')

    submission = collection.find({
        'kq': assignment.kq.id,
        'assigned_to': user_id
    })

    if submission.count() == 0:
        messages.error(request, _('You don\'t have this submission assigned.'))
        return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

    submission_obj = submission[0]

    submitter = User.objects.get(id=int(submission_obj['author']))

    criteria_initial = [{'evaluation_criterion_id': criterion.id} for criterion in assignment.criteria.all()]
    EvalutionCriteriaResponseFormSet = formset_factory(EvalutionCriteriaResponseForm, extra=0, max_num=len(criteria_initial))

    if request.method == "POST":
        submission_form = ReviewSubmissionForm(request.POST)
        criteria_formset = EvalutionCriteriaResponseFormSet(request.POST, initial=criteria_initial)
        if criteria_formset.is_valid() and submission_form.is_valid():
            criteria_values = [(int(form.cleaned_data['evaluation_criterion_id']), int(form.cleaned_data['value'])) for form in criteria_formset]
            try:
                review = save_review(assignment.kq, request.user, submitter, criteria_values, submission_form.cleaned_data['comments'])
                current_site_name = get_current_site(request).name
                send_mail_to_submission_owner(current_site_name, assignment, review, submitter)
            except IntegrityError:
                messages.error(request, _('Your can\'t submit two times the same review.'))
                return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

            reviews = get_db().get_collection('peer_review_reviews')
            reviewed = reviews.find({
                    'reviewer': user_id,
                    'kq': assignment.kq.id,
                    })
            pending = assignment.minimum_reviewers - reviewed.count()
            if pending > 0:
                messages.success(request, _('Your review has been submitted. You have to review at least %d exercises more.') % pending)
            else:
                messages.success(request, _('Your review has been submitted.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
    else:
        submission_form = ReviewSubmissionForm()
        criteria_formset = EvalutionCriteriaResponseFormSet(initial=criteria_initial)

    return render_to_response('peerreview/review_review.html', {
            'submission': submission[0],
            'submission_form': submission_form,
            'criteria_formset': criteria_formset,
            'course': course,
            'assignment': assignment,
            }, context_instance=RequestContext(request))

def send_mail_to_submission_owner(current_site_name, assignment, review, submitter):
    subject = _(u'Your assignment "%(nugget)s" has been reviewed') % {'nugget': assignment.kq.title}
    template = 'peerreview/email_review_submission.txt'
    review_criteria = []
    for item in review['criteria']:
        try:
            criterion = EvaluationCriterion.objects.get(pk=item[0]).title
        except:
            criterion = _(u'Undefined')

        review_criteria.append((criterion, item[1]))

    context = {
        'user': submitter,
        'date': review['created'].strftime('%d/%m/%Y'),
        'nugget': assignment.kq.title,
        'review_criteria': review_criteria,
        'comment': review['comment'],
        'site': current_site_name
    }
    to = [submitter.email]

    send_mail_wrapper(subject, template, context, to)


@login_required
def get_s3_upload_url(request):
    user = request.user

    filename = request.GET.get('name', 'noname')
    kq_id = request.GET.get('kq', 'nokq')

    name = "%d/%s/%s" % (user.id, kq_id, filename)
    mime_type = request.GET['type']

    expires = time.time() + settings.AWS_S3_UPLOAD_EXPIRE_TIME
    amz_headers = "x-amz-acl:public-read"
    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, settings.AWS_STORAGE_BUCKET_NAME, name)

    sig = hmac.new(settings.AWS_SECRET_ACCESS_KEY, string_to_sign, hashlib.sha1).digest()
    sig = base64.encodestring(sig).strip()
    sig = urllib.quote(sig, safe='')

    url = "%s/%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s" % (
        settings.AWS_S3_URL,
        name,
        settings.AWS_ACCESS_KEY_ID,
        expires,
        sig
    )

    return HttpResponse(urllib.quote(url))


@login_required
def get_s3_download_url(request):
    name = request.GET.get('name', 'noname')
    kq_id = request.GET.get('kq', 'nokq')
    url = s3_url(request.user.id, name, kq_id)
    return HttpResponse(urllib.quote(url))


def s3_url(user_id, filename, kq_id):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = boto.s3.key.Key(bucket)
    name = "%d/%s/%s" % (user_id, kq_id, filename)
    k.key = name
    return k.generate_url(expires_in=60*60*24*365*10) # 10 years


def s3_upload(user_id, kq_id, filename, file_obj):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = boto.s3.key.Key(bucket)
    name = "%d/%s/%s" % (user_id, kq_id, filename)
    k.key = name
    k.set_contents_from_file(file_obj)


@login_required
def course_review_upload(request, course_slug):
    if request.method == "POST":
        course = get_object_or_404(Course, slug=course_slug)

        file_to_upload = request.FILES.get('pr_file', None)
        submission_text = request.POST.get('pr-submission', '')

        kq = get_object_or_404(KnowledgeQuantum, id=request.POST.get('kq_id', 0))
        unit = kq.unit

        if (file_to_upload.size / (1024 * 1024) >= settings.PEER_REVIEW_FILE_MAX_SIZE):
            messages.error(request, _('Your file is greater than the max allowed size (%d MB).') % settings.PEER_REVIEW_FILE_MAX_SIZE)
            return HttpResponseRedirect(reverse('course_classroom', args=[course_slug])+"#unit%d/kq%d/p" % (unit.id, kq.id))

        if (len(submission_text) >= settings.PEER_REVIEW_TEXT_MAX_SIZE):
            messages.error(request, _('Your text is greater than the max allowed size (%d characters).') % settings.PEER_REVIEW_TEXT_MAX_SIZE)
            return HttpResponseRedirect(reverse('course_classroom', args=[course_slug])+"#unit%d/kq%d/p" % (unit.id, kq.id))

        s3_upload(request.user.id, kq.id, file_to_upload.name, file_to_upload)
        file_url = s3_url(request.user.id, file_to_upload.name, kq.id)

        submission = {
            "author": request.user.id,
            "author_reviews": 0,
            "text": request.POST.get('pr-submission', ''),
            "file": file_url,
            "created": datetime.now(),
            "reviewers": [],
            "reviews": 0,
            "course": course.id,
            "unit": unit.id,
            "kq": kq.id,
            "assigned_to": None,
        }
        db = get_db()
        submissions = db.get_collection("peer_review_submissions")
        submissions.insert(submission)

        return HttpResponseRedirect(reverse('course_classroom', args=[course_slug])+"#unit%d/kq%d" % (unit.id, kq.id))
