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
import urllib

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
from django.utils.decorators import method_decorator
from django.views.generic import View

from moocng.api.mongodb import get_db
from moocng.api.tasks import on_peerreviewreview_created_task
from moocng.courses.models import Course, KnowledgeQuantum
from moocng.courses.utils import send_mail_wrapper, is_course_ready
from moocng.peerreview.forms import ReviewSubmissionForm, EvalutionCriteriaResponseForm
from moocng.peerreview.models import PeerReviewAssignment, EvaluationCriterion
from moocng.peerreview.utils import course_get_visible_peer_review_assignments, save_review


class CourseReviewAssign(View):
    def get(self, request, course_slug, assignment_id):
        return self.get_and_post(request, course_slug, assignment_id)

    def post(self, request, course_slug, assignment_id):
        return self.get_and_post(request, course_slug, assignment_id)

    def get_and_post(self, request, course_slug, assignment_id):
        course = get_object_or_404(Course, slug=course_slug)
        assignment = get_object_or_404(PeerReviewAssignment, id=assignment_id)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        if assignment.kq.unit.course != course:
            messages.error(request, _('The selected peer review assignment is not part of this course.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        self.collection = get_db().get_collection('peer_review_submissions')

        submission = self.get_assigned_submissions(assignment.kq, request.user)

        if submission.count() > 0:
            messages.error(request, _('You already have a submission assigned.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        submission = self.get_available_submission(assignment.kq, request.user)

        if submission.count() == 0:
            messages.error(request, _('There is no submission avaliable for you at this moment. Please, try again later.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))
        else:
            self.assign_submission(submission[0], request.user)
            return HttpResponseRedirect(reverse('course_review_review', args=[course_slug, assignment_id]))

    def assign_submission(self, submission, user):
        self.collection.update({
            '_id': submission['_id']
        }, {
            '$set': {
                'assigned_to': user.id,
                'assigned_when': datetime.utcnow()
            }
        })

    def get_assigned_submissions(self, kq, user):
        return self.collection.find({
            'kq': kq.id,
            'assigned_to': user.id
        })

    def get_available_submission(self, kq, user):
        max_hours_assigned = timedelta(
            hours=getattr(settings, "PEER_REVIEW_ASSIGNATION_EXPIRE", 24)
        )
        assignation_expire = datetime.utcnow() - max_hours_assigned

        return self.collection.find({
            'kq': kq.id,
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
                '$ne': user.id
            },
            'reviewers': {
                '$ne': user.id
            }
        }).sort([
            ('reviews', pymongo.ASCENDING),
            ('author_reviews', pymongo.DESCENDING),
        ]).limit(1)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseReviewAssign, self).dispatch(*args, **kwargs)


class CourseReview(View):
    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        is_ready, ask_admin = is_course_ready(course)

        if not is_ready:
            return render_to_response('courses/no_content.html', {
                'course': course,
                'is_enrolled': is_enrolled,
                'ask_admin': ask_admin,
            }, context_instance=RequestContext(request))

        assignments = course_get_visible_peer_review_assignments(request.user,
                                                                 course)

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
            'is_enrolled': is_enrolled,
        }, context_instance=RequestContext(request))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseReview, self).dispatch(*args, **kwargs)

class CourseReviewReview(View):
    def get(self, request, course_slug, assignment_id):
        course = get_object_or_404(Course, slug=course_slug)
        assignment = get_object_or_404(PeerReviewAssignment, id=assignment_id)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        if assignment.kq.unit.course != course:
            messages.error(request, _('The selected peer review assignment is not part of this course.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        collection = get_db().get_collection('peer_review_submissions')

        submission = collection.find({
            'kq': assignment.kq.id,
            'assigned_to': request.user.id
        })

        if submission.count() == 0:
            messages.error(request, _('You don\'t have this submission assigned.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        submission_obj = submission[0]

        submitter = User.objects.get(id=int(submission_obj['author']))

        criteria_initial = [{'evaluation_criterion_id': criterion.id} for criterion in assignment.criteria.all()]
        EvalutionCriteriaResponseFormSet = formset_factory(EvalutionCriteriaResponseForm, extra=0, max_num=len(criteria_initial))

        submission_form = ReviewSubmissionForm()
        criteria_formset = EvalutionCriteriaResponseFormSet(initial=criteria_initial)

        max_hours_assigned = timedelta(hours=getattr(settings,
                                       "PEER_REVIEW_ASSIGNATION_EXPIRE", 24))

        assigned_when = submission[0]["assigned_when"]
        assignation_expire = assigned_when + max_hours_assigned

        now = datetime.now(assigned_when.tzinfo)
        is_assignation_expired = now > assignation_expire

        return render_to_response('peerreview/review_review.html', {
            'submission': submission[0],
            'is_assignation_expired': is_assignation_expired,
            'assignation_expire': assignation_expire,
            'submission_form': submission_form,
            'criteria_formset': criteria_formset,
            'course': course,
            'assignment': assignment,
            'is_enrolled': is_enrolled,
        }, context_instance=RequestContext(request))

    def post(self, request, course_slug, assignment_id):
        course = get_object_or_404(Course, slug=course_slug)
        assignment = get_object_or_404(PeerReviewAssignment, id=assignment_id)

        is_enrolled = course.students.filter(id=request.user.id).exists()
        if not is_enrolled:
            messages.error(request, _('You are not enrolled in this course'))
            return HttpResponseRedirect(reverse('course_overview', args=[course_slug]))

        if assignment.kq.unit.course != course:
            messages.error(request, _('The selected peer review assignment is not part of this course.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        collection = get_db().get_collection('peer_review_submissions')

        submission = collection.find({
            'kq': assignment.kq.id,
            'assigned_to': request.user.id
        })

        if submission.count() == 0:
            messages.error(request, _('You don\'t have this submission assigned.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        submission_obj = submission[0]

        submitter = User.objects.get(id=int(submission_obj['author']))

        criteria_initial = [{'evaluation_criterion_id': criterion.id} for criterion in assignment.criteria.all()]
        EvalutionCriteriaResponseFormSet = formset_factory(EvalutionCriteriaResponseForm, extra=0, max_num=len(criteria_initial))

        submission_form = ReviewSubmissionForm(request.POST)
        criteria_formset = EvalutionCriteriaResponseFormSet(request.POST, initial=criteria_initial)
        if criteria_formset.is_valid() and submission_form.is_valid():
            criteria_values = [(int(form.cleaned_data['evaluation_criterion_id']), int(form.cleaned_data['value'])) for form in criteria_formset]
            try:
                review = save_review(assignment.kq, request.user, submitter, criteria_values, submission_form.cleaned_data['comments'])

                reviews = get_db().get_collection('peer_review_reviews')
                reviewed_count = reviews.find({
                    'reviewer': request.user.id,
                    'kq': assignment.kq.id
                }).count()
                on_peerreviewreview_created_task.apply_async(
                    args=[review, reviewed_count],
                    queue='stats',
                )

                current_site_name = get_current_site(request).name
                self.send_mail_to_submission_owner(current_site_name, assignment, review, submitter)
            except IntegrityError:
                messages.error(request, _('Your can\'t submit two times the same review.'))
                return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

            pending = assignment.minimum_reviewers - reviewed_count
            if pending > 0:
                messages.success(request, _('Your review has been submitted. You have to review at least %d exercises more.') % pending)
            else:
                messages.success(request, _('Your review has been submitted.'))
            return HttpResponseRedirect(reverse('course_reviews', args=[course_slug]))

        max_hours_assigned = timedelta(hours=getattr(settings,
                                       "PEER_REVIEW_ASSIGNATION_EXPIRE", 24))

        assigned_when = submission[0]["assigned_when"]
        assignation_expire = assigned_when + max_hours_assigned

        now = datetime.now(assigned_when.tzinfo)
        is_assignation_expired = now > assignation_expire

        return render_to_response('peerreview/review_review.html', {
            'submission': submission[0],
            'is_assignation_expired': is_assignation_expired,
            'assignation_expire': assignation_expire,
            'submission_form': submission_form,
            'criteria_formset': criteria_formset,
            'course': course,
            'assignment': assignment,
            'is_enrolled': is_enrolled,
        }, context_instance=RequestContext(request))

    def send_mail_to_submission_owner(self, current_site_name, assignment, review, submitter):
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseReviewReview, self).dispatch(*args, **kwargs)


class GetS3UploadUrl(View):
    def get(self, request):
        user = request.user

        filename = request.GET.get('name', 'noname')
        kq_id = request.GET.get('kq', 'nokq')

        name = "%d/%s/%s" % (user.id, kq_id, filename)
        mime_type = request.GET['type']
        headers = {
            'x-amz-acl': "public-read",
            'Content-Type': mime_type,
        }

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        url = conn.generate_url(
            settings.AWS_S3_UPLOAD_EXPIRE_TIME,
            "PUT",
            settings.AWS_STORAGE_BUCKET_NAME,
            name,
            headers
        )

        return HttpResponse(urllib.quote(url))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetS3UploadUrl, self).dispatch(*args, **kwargs)


class BaseS3UtilView(View):
    def s3_url(self, user_id, filename, kq_id):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = boto.s3.key.Key(bucket)
        name = "%d/%s/%s" % (user_id, kq_id, filename)
        k.key = name
        return k.generate_url(expires_in=0, query_auth=False)

    def s3_upload(self, user_id, kq_id, filename, file_obj):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        k = boto.s3.key.Key(bucket)
        name = "%d/%s/%s" % (user_id, kq_id, filename)
        k.key = name
        k.set_contents_from_file(file_obj)
        k.make_public()


class GetS3DownloadUrl(BaseS3UtilView):
    def get(self, request):
        name = request.GET.get('name', 'noname')
        kq_id = request.GET.get('kq', 'nokq')
        url = self.s3_url(request.user.id, name, kq_id)
        return HttpResponse(urllib.quote(url))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetS3DownloadUrl, self).dispatch(*args, **kwargs)


class CourseReviewUpload(BaseS3UtilView):
    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        file_to_upload = request.FILES.get('pr_file', None)
        submission_text = request.POST.get('pr-submission', '')

        kq = get_object_or_404(KnowledgeQuantum, id=request.POST.get('kq_id', 0))
        unit = kq.unit

        if (file_to_upload.size / (1024 * 1024) >= settings.PEER_REVIEW_FILE_MAX_SIZE):
            messages.error(request, _('Your file is greater than the max allowed size (%d MB).') % settings.PEER_REVIEW_FILE_MAX_SIZE)
            return HttpResponseRedirect(reverse('course_classroom', args=[course_slug]) + "#unit%d/kq%d/p" % (unit.id, kq.id))

        if (len(submission_text) >= settings.PEER_REVIEW_TEXT_MAX_SIZE):
            messages.error(request, _('Your text is greater than the max allowed size (%d characters).') % settings.PEER_REVIEW_TEXT_MAX_SIZE)
            return HttpResponseRedirect(reverse('course_classroom', args=[course_slug]) + "#unit%d/kq%d/p" % (unit.id, kq.id))

        self.s3_upload(request.user.id, kq.id, file_to_upload.name, file_to_upload)
        file_url = self.s3_url(request.user.id, file_to_upload.name, kq.id)

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

        return HttpResponseRedirect(reverse('course_classroom', args=[course_slug]) + "#unit%d/kq%d/p" % (unit.id, kq.id))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseReviewUpload, self).dispatch(*args, **kwargs)
