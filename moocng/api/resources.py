# -*- coding: utf-8 -*-

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


from datetime import datetime
import re

from bson import ObjectId
from bson.errors import InvalidId

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import NotFound, BadRequest
from tastypie.resources import ModelResource

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponse

from moocng.api.authentication import (DjangoAuthentication,
                                       TeacherAuthentication,
                                       ApiKeyAuthentication,
                                       MultiAuthentication)
from moocng.api.authorization import (PublicReadTeachersModifyAuthorization,
                                      TeacherAuthorization,
                                      UserResourceAuthorization)
from moocng.api.mongodb import get_user, MongoObj, MongoResource
from moocng.api.validation import (AnswerValidation,
                                   PeerReviewSubmissionsResourceValidation)
from moocng.courses.models import (Unit, KnowledgeQuantum, Question, Option,
                                   Attachment, Course)
from moocng.courses.utils import normalize_kq_weight, calculate_course_mark
from moocng.mongodb import get_db
from moocng.peerreview.models import PeerReviewAssignment, EvaluationCriterion
from moocng.peerreview.utils import (kq_get_peer_review_score,
                                     get_peer_review_review_score)
from moocng.videos.utils import extract_YT_video_id

from moocng.assets.models import Asset


class CourseResource(ModelResource):

    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        allowed_methods = ['get']
        excludes = ['certification_banner']
        authentication = MultiAuthentication(DjangoAuthentication(), ApiKeyAuthentication())
        authorization = DjangoAuthorization()


class UnitResource(ModelResource):
    course = fields.ToOneField(CourseResource, 'course')

    class Meta:
        queryset = Unit.objects.all()
        resource_name = 'unit'
        authentication = DjangoAuthentication()
        authorization = PublicReadTeachersModifyAuthorization()
        always_return_data = True
        filtering = {
            "course": ('exact'),
        }

    def alter_deserialized_detail_data(self, request, data):
        if u'title' in data and data[u'title'] is not None:
            data[u'title'] = data[u'title'].strip()
        return data


class KnowledgeQuantumResource(ModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.ToManyField('moocng.api.resources.QuestionResource',
                                  'question_set', related_name='kq',
                                  readonly=True, null=True)
    peer_review_assignment = fields.ToOneField(
        'moocng.api.resources.PeerReviewAssignmentResource',
        'peerreviewassignment',
        related_name='peer_review_assignment',
        readonly=True, null=True)
    peer_review_score = fields.IntegerField(readonly=True)
    videoID = fields.CharField(readonly=True)
    correct = fields.BooleanField(readonly=True)
    completed = fields.BooleanField(readonly=True)
    normalized_weight = fields.IntegerField(readonly=True)

    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'kq'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "unit": ('exact'),
        }

    def get_object_list(self, request):
        objects = super(KnowledgeQuantumResource, self).get_object_list(request)
        return objects.filter(
            Q(unit__unittype='n') |
            Q(unit__start__isnull=True) |
            Q(unit__start__isnull=False, unit__start__lte=datetime.now)
        )

    def dispatch(self, request_type, request, **kwargs):
        db = get_db()
        self.user_answers = get_user(request, db.get_collection('answers'))
        self.user_activity = get_user(request, db.get_collection('activity'))
        return super(KnowledgeQuantumResource, self).dispatch(request_type,
                                                              request,
                                                              **kwargs)

    def dehydrate_normalized_weight(self, bundle):
        return normalize_kq_weight(bundle.obj)

    def dehydrate_question(self, bundle):
        question = bundle.data['question']
        if len(question) == 0:
            return None
        else:
            return question[0]

    def dehydrate_peer_review_score(self, bundle):
        try:
            return kq_get_peer_review_score(bundle.obj, bundle.request.user)
        except ObjectDoesNotExist:
            return None

    def dehydrate_videoID(self, bundle):
        return extract_YT_video_id(bundle.obj.video)

    def dehydrate_correct(self, bundle):
        questions = bundle.obj.question_set.all()
        if questions.count() == 0:
            # no question: a kq is correct if it is completed
            try:
                return bundle.obj.is_completed(bundle.request.user)
            except AttributeError:
                return False
        else:
            question = questions[0]  # there should be only one question
            if self.user_answers is None:
                return False

            answer = self.user_answers.get('questions', {}).get(unicode(question.id))
            if answer is None:
                return False

            return question.is_correct(answer)

    def dehydrate_completed(self, bundle):
        return bundle.obj.is_completed(bundle.request.user)


class PrivateKnowledgeQuantumResource(ModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.ToManyField('moocng.api.resources.QuestionResource',
                                  'question_set', related_name='kq',
                                  readonly=True, null=True)
    peer_review_assignment = fields.ToOneField(
        'moocng.api.resources.PeerReviewAssignmentResource',
        'peerreviewassignment',
        related_name='peer_review_assignment',
        readonly=True, null=True)
    videoID = fields.CharField()
    normalized_weight = fields.IntegerField()

    class Meta:
        queryset = KnowledgeQuantum.objects.all()
        resource_name = 'privkq'
        always_return_data = True
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "unit": ('exact'),
        }

    def alter_deserialized_detail_data(self, request, data):
        if u'title' in data and data[u'title'] is not None:
            data[u'title'] = data[u'title'].strip()
        return data

    def dehydrate_normalized_weight(self, bundle):
        return normalize_kq_weight(bundle.obj)

    def dehydrate_question(self, bundle):
        question = bundle.data['question']
        if len(question) == 0:
            return None
        else:
            return question[0]

    def dehydrate_videoID(self, bundle):
        return extract_YT_video_id(bundle.obj.video)

    def hydrate_videoID(self, bundle):
        if 'videoID' in bundle.data and bundle.data['videoID'] is not None:
            video = 'http://youtu.be/' + bundle.data['videoID']
            bundle.data['video'] = video
        return bundle


class AttachmentResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = Attachment.objects.all()
        resource_name = 'attachment'
        authentication = DjangoAuthentication()
        authorization = PublicReadTeachersModifyAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def dehydrate_attachment(self, bundle):
        return bundle.obj.attachment.url


class PeerReviewAssignmentResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = PeerReviewAssignment.objects.all()
        resource_name = 'peer_review_assignment'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def get_object_list(self, request):
        objects = super(PeerReviewAssignmentResource, self).get_object_list(request)
        return objects.filter(
            Q(kq__unit__unittype='n') |
            Q(kq__unit__start__isnull=True) |
            Q(kq__unit__start__isnull=False, kq__unit__start__lte=datetime.now)
        )


class PrivatePeerReviewAssignmentResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = PeerReviewAssignment.objects.all()
        resource_name = 'privpeer_review_assignment'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def obj_delete(self, request, **kwargs):
        obj = self.obj_get(request, **kwargs)
        #submissions and reviews must be deleted too
        submissions = get_db().get_collection('peer_review_submissions')
        submissions.remove({'kq': obj.kq_id})
        reviews = get_db().get_collection('peer_review_reviews')
        reviews.remove({'kq': obj.kq_id})
        super(PrivatePeerReviewAssignmentResource, self).obj_delete(request, **kwargs)


class EvaluationCriterionResource(ModelResource):
    assignment = fields.ToOneField(PeerReviewAssignmentResource, 'assignment')

    class Meta:
        queryset = EvaluationCriterion.objects.all()
        resource_name = 'evaluation_criterion'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "assignment": ('exact'),
            "unit": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):

        assignment = request.GET.get('assignment', None)
        unit = request.GET.get('unit', None)

        if assignment is not None:
            results = EvaluationCriterion.objects.filter(assignment_id=assignment)
        elif unit is not None:
            results = EvaluationCriterion.objects.filter(assignment__kq__unit_id=unit)
        else:
            results = EvaluationCriterion.objects.all()
        return results.filter(
            Q(assignment__kq__unit__unittype='n') |
            Q(assignment__kq__unit__start__isnull=True) |
            Q(assignment__kq__unit__start__isnull=False, assignment__kq__unit__start__lte=datetime.now)
        )


class PrivateEvaluationCriterionResource(ModelResource):
    assignment = fields.ToOneField(PeerReviewAssignmentResource, 'assignment')

    class Meta:
        queryset = EvaluationCriterion.objects.all()
        resource_name = 'privevaluation_criterion'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "assignment": ('exact'),
            "unit": ('exact'),
        }

    def alter_deserialized_detail_data(self, request, data):
        if u'title' in data and data[u'title'] is not None:
            data[u'title'] = data[u'title'].strip()
        if u'description' in data and data[u'description'] is not None:
            data[u'description'] = data[u'description'].strip()
        return data

    def obj_get_list(self, request=None, **kwargs):

        assignment = request.GET.get('assignment', None)
        unit = request.GET.get('unit', None)

        if assignment is not None:
            results = EvaluationCriterion.objects.filter(assignment_id=assignment)
        elif unit is not None:
            results = EvaluationCriterion.objects.filter(assignment__kq__unit_id=unit)
        else:
            results = EvaluationCriterion.objects.all()
        return results


class PeerReviewSubmissionsResource(MongoResource):
    class Meta:
        resource_name = 'peer_review_submissions'
        collection = 'peer_review_submissions'
        datakey = 'peer_review_submissions'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        validation = PeerReviewSubmissionsResourceValidation()
        allowed_methods = ['get', 'post']
        filtering = {
            "kq": ('exact'),
            "unit": ('exact'),
            "course": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):

        mongo_query = {
            "author": request.GET.get('author', request.user.id)
        }

        for key in self._meta.filtering.keys():
            if key in request.GET:
                try:
                    mongo_query[key] = int(request.GET.get(key))
                except ValueError:
                    mongo_query[key] = request.GET.get(key)

        query_results = self._collection.find(mongo_query)

        results = []

        for query_item in query_results:
            obj = MongoObj(initial=query_item)
            obj.uuid = query_item["_id"]
            results.append(obj)

        return results

    def obj_get(self, request=None, **kwargs):

        try:
            query = dict(_id=ObjectId(kwargs['pk']))
        except InvalidId:
            raise BadRequest('Invalid ObjectId provided')

        mongo_item = self._collection.find_one(query)

        if mongo_item is None:
            raise NotFound('Invalid resource lookup data provided')

        obj = MongoObj(initial=mongo_item)
        obj.uuid = kwargs['pk']
        return obj

    def obj_create(self, bundle, request=None, **kwargs):

        bundle = self.full_hydrate(bundle)

        if "bundle" not in bundle.data and "reviews" not in bundle.data:
            kq = KnowledgeQuantum.objects.get(id=int(bundle.data["kq"]))

            if "unit" not in bundle.data:
                bundle.data["unit"] = kq.unit.id

            if "course" not in bundle.data:
                bundle.data["course"] = kq.unit.course.id

        if "created" not in bundle.data:
            bundle.data["created"] = datetime.utcnow()

        bundle.data["reviews"] = 0
        bundle.data["author_reviews"] = 0
        bundle.data["author"] = request.user.id

        self._collection.insert(bundle.data, safe=True)

        bundle.uuid = bundle.obj.uuid

        return bundle


class PeerReviewReviewsResource(MongoResource):
    score = fields.IntegerField(readonly=True)

    class Meta:
        resource_name = 'peer_review_reviews'
        collection = 'peer_review_reviews'
        datakey = 'peer_review_reviews'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get']
        filtering = {
            "reviewer": ('exact'),
            "kq": ('exact'),
            "unit": ('exact'),
            "course": ('exact'),
            "submission_id": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):
        mongo_query = {
            "author": request.GET.get('author', request.user.id)
        }

        for key in self._meta.filtering.keys():
            if key in request.GET:
                try:
                    mongo_query[key] = int(request.GET.get(key))
                except ValueError:
                    mongo_query[key] = request.GET.get(key)

        query_results = self._collection.find(mongo_query)

        results = []

        for query_item in query_results:
            obj = MongoObj(initial=query_item)
            obj.uuid = query_item["_id"]
            results.append(obj)

        return results

    def obj_get(self, request=None, **kwargs):

        try:
            query = dict(_id=ObjectId(kwargs['pk']))
        except InvalidId:
            raise BadRequest('Invalid ObjectId provided')

        mongo_item = self._collection.find_one(query)

        if mongo_item is None:
            raise NotFound('Invalid resource lookup data provided')

        obj = MongoObj(initial=mongo_item)
        obj.uuid = kwargs['pk']
        return obj

    def dehydrate_score(self, bundle):
        return get_peer_review_review_score(bundle.obj.to_dict())


class QuestionResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')
    solutionID = fields.CharField(readonly=True)

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def get_object_list(self, request):
        objects = super(QuestionResource, self).get_object_list(request)
        return objects.filter(
            Q(kq__unit__unittype='n') |
            Q(kq__unit__start__isnull=True) |
            Q(kq__unit__start__isnull=False, kq__unit__start__lte=datetime.now)
        )

    def dehydrate_solution_video(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if unit.unittype != 'n' and unit.deadline > datetime.now(unit.deadline.tzinfo):
            return None
        return bundle.obj.solution_video

    def dehydrate_solutionID(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if unit.unittype != 'n' and unit.deadline > datetime.now(unit.deadline.tzinfo):
            return None
        return extract_YT_video_id(bundle.obj.solution_video)

    def dehydrate_solution_text(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if unit.unittype != 'n' and unit.deadline > datetime.now(unit.deadline.tzinfo):
            return None
        return bundle.obj.solution_text

    def dehydrate_last_frame(self, bundle):
        try:
            return bundle.obj.last_frame.url
        except ValueError:
            return "%simg/no-image.png" % settings.STATIC_URL


class PrivateQuestionResource(ModelResource):
    kq = fields.ToOneField(PrivateKnowledgeQuantumResource, 'kq')
    solutionID = fields.CharField()

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'privquestion'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        always_return_data = True
        filtering = {
            "kq": ('exact'),
        }

    def dehydrate_solutionID(self, bundle):
        return extract_YT_video_id(bundle.obj.solution_video)

    def dehydrate_last_frame(self, bundle):
        try:
            return bundle.obj.last_frame.url
        except ValueError:
            return "%simg/no-image.png" % settings.STATIC_URL

    def hydrate(self, bundle):
        try:
            bundle.obj.last_frame.file
        except ValueError:
            bundle.obj.last_frame = ImageFieldFile(
                bundle.obj, Question._meta.get_field_by_name('last_frame')[0],
                "")
        return bundle

    def hydrate_solutionID(self, bundle):
        if 'solutionID' in bundle.data and bundle.data['solutionID'] is not None:
            if bundle.data['solutionID'] != '':
                bundle.data['solution_video'] = 'http://youtu.be/' + bundle.data['solutionID']
            else:
                bundle.data['solution_video'] = ''
        return bundle


class OptionResource(ModelResource):
    question = fields.ToOneField(QuestionResource, 'question')

    class Meta:
        queryset = Option.objects.all()
        resource_name = 'option'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "question": ('exact'),
        }

    def get_object_list(self, request):
        objects = super(OptionResource, self).get_object_list(request)
        return objects.filter(
            Q(question__kq__unit__unittype='n') |
            Q(question__kq__unit__start__isnull=True) |
            Q(question__kq__unit__start__isnull=False, question__kq__unit__start__lte=datetime.now)
        )

    def dispatch(self, request_type, request, **kwargs):
        # We need the request to dehydrate some fields
        collection = get_db().get_collection('answers')
        self.user = get_user(request, collection)
        return super(OptionResource, self).dispatch(request_type, request,
                                                    **kwargs)

    def dehydrate_solution(self, bundle):
        # Only return the solution if the user has given an answer
        # If there is a deadline, then only return the solution if the deadline
        # has been reached too
        solution = None
        if self.user:
            answer = self.user['questions'].get(
                unicode(bundle.obj.question.id), None)
            if answer is not None:
                unit = bundle.obj.question.kq.unit
                if unit.unittype == 'n' or not(unit.deadline and datetime.now(unit.deadline.tzinfo) < unit.deadline):
                    solution = bundle.obj.solution
        return solution

    def dehydrate_feedback(self, bundle):
        # Only return the feedback if the user has given an answer
        feedback = None
        if self.user:
            answer = self.user['questions'].get(
                unicode(bundle.obj.question.id), None)
            if answer is not None:
                feedback = bundle.obj.feedback
        return feedback


class AnswerResource(MongoResource):

    class Meta:
        resource_name = 'answer'
        collection = 'answers'
        datakey = 'questions'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "question": ('exact'),
        }
        validation = AnswerValidation()

    def obj_get_list(self, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)
        question_id = request.GET.get('question', None)

        results = []
        if question_id is None:
            for qid, question in user['questions'].items():
                if qid == question_id:
                    obj = MongoObj(initial=question)
                    obj.uuid = question_id
                    results.append(obj)
        else:
            question = user['questions'].get(question_id, None)
            if question is not None:
                obj = MongoObj(initial=question)
                obj.uuid = question_id
                results.append(obj)

        return results

    def obj_create(self, bundle, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)

        bundle = self.full_hydrate(bundle)

        unit = Question.objects.get(id=bundle.obj.uuid).kq.unit
        if unit.unittype != 'n' and unit.deadline and datetime.now(unit.deadline.tzinfo) > unit.deadline:
            return bundle

        if (len(bundle.obj.answer['replyList']) > 0):
            user['questions'][bundle.obj.uuid] = bundle.obj.answer

            self._collection.update({'_id': user['_id']}, user, safe=True)

        bundle.uuid = bundle.obj.uuid

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def hydrate(self, bundle):
        if 'question' in bundle.data:
            question = bundle.data['question']
            pattern = (r'^/api/%s/question/(?P<question_id>\d+)/$' %
                       self._meta.api_name)
            result = re.findall(pattern, question)
            if result and len(result) == 1:
                bundle.obj.uuid = result[0]

        bundle.obj.answer = {}

        if 'date' in bundle.data:
            bundle.obj.answer['date'] = bundle.data['date']

        if 'replyList' in bundle.data:
            bundle.obj.answer['replyList'] = bundle.data['replyList']

        return bundle

    def dehydrate(self, bundle):
        bundle.data['date'] = bundle.obj.date
        bundle.data['replyList'] = bundle.obj.replyList
        return bundle


class ActivityResource(MongoResource):

    class Meta:
        resource_name = 'activity'
        collection = 'activity'
        datakey = 'courses'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'put']
        filtering = {
            "unit": ('exact'),
        }
        validation = AnswerValidation()

    def obj_update(self, bundle, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)
        course_id = kwargs['pk']

        bundle = self.full_hydrate(bundle)

        user[self._meta.datakey][course_id] = bundle.obj.kqs

        self._collection.update({'_id': user['_id']}, user, safe=True)

        bundle.uuid = bundle.obj.uuid

        return bundle

    def hydrate(self, bundle):
        bundle.obj.kqs = {}
        if 'kqs' in bundle.data:
            bundle.obj.kqs['kqs'] = bundle.data['kqs']

        return bundle

    def dehydrate(self, bundle):
        bundle.data['kqs'] = bundle.obj.kqs
        return bundle

    def _initial(self, request, **kwargs):
        course_id = kwargs['pk']
        return {course_id: {'kqs': []}}


class UserResource(ModelResource):

    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        allowed_methods = ['get']
        authentication = MultiAuthentication(TeacherAuthentication(),
                                             ApiKeyAuthentication())
        authorization = UserResourceAuthorization()
        fields = ['id', 'email', 'first_name', 'last_name']
        filtering = {
            'first_name': ['istartswith'],
            'last_name': ['istartswith'],
            'email': ('exact')
        }

    def apply_filters(self, request, applicable_filters):
        applicable_filters = applicable_filters.items()
        if len(applicable_filters) > 0:
            Qfilter = Q(applicable_filters[0])
            for apfilter in applicable_filters[1:]:
                Qfilter = Qfilter | Q(apfilter)
            return self.get_object_list(request).filter(Qfilter)
        else:
            return self.get_object_list(request)

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>[^/]+)/allcourses/$" % self._meta.resource_name,
                self.wrap_view('get_courses'), name="get_courses_as_student"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[^/]+)/passedcourses/$" % self._meta.resource_name,
                self.wrap_view('get_passed_courses'),
                name="get_passed_courses_as_student"),
        ]

    def get_object(self, request, kwargs):
        try:
            if not kwargs['pk'].isdigit():
                kwargs['email'] = kwargs['pk']
                del kwargs['pk']
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except self.Meta.object_class.DoesNotExist:
            return HttpResponse(status=404)
        return obj

    def alt_get_list(self, request, courses):
        resource = CourseResource()

        sorted_objects = resource.apply_sorting(courses,
                                                options=request.GET)
        paginator = resource._meta.paginator_class(
            request.GET, sorted_objects,
            resource_uri=resource.get_resource_list_uri(),
            limit=resource._meta.limit)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [resource.build_bundle(obj=obj, request=request)
                   for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [resource.full_dehydrate(bundle)
                                       for bundle in bundles]
        to_be_serialized = resource.alter_list_data_to_serialize(
            request, to_be_serialized)
        return resource.create_response(request, to_be_serialized)

    def get_courses(self, request, **kwargs):
        self.is_authenticated(request)
        self.is_authorized(request)
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj
        courses = obj.courses_as_student.all()
        return self.alt_get_list(request, courses)

    def get_passed_courses(self, request, **kwargs):
        # In tastypie, the override_urls don't call Authentication/Authorization
        self.is_authenticated(request)
        self.is_authorized(request)
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj
        passed_courses = []
        if 'courseid' in request.GET:
            courseid = int(request.GET.get('courseid'))
            courses = obj.courses_as_student.filter(id=courseid)
        else:
            courses = obj.courses_as_student.all()
        for course in courses:
            if course.threshold is not None:
                total_mark, units_info = calculate_course_mark(course, obj)
                if float(course.threshold) <= total_mark:
                    passed_courses.append(course)
        return self.alt_get_list(request, passed_courses)
    

class AssetResource(ModelResource):

    class Meta:
        queryset = Asset.objects.all()
        resource_name = 'asset'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
