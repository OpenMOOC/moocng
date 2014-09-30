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


from datetime import datetime, date, timedelta
import logging
import sys

from bson import ObjectId
from bson.errors import InvalidId

from tastypie import fields
from tastypie import http
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import NotFound, BadRequest
from tastypie.resources import ModelResource, Resource
from tastypie.utils.mime import build_content_type


from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q, Count
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
from django.utils.cache import patch_cache_control
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from moocng.api.authentication import (DjangoAuthentication,
                                       TeacherAuthentication,
                                       ApiKeyAuthentication,
                                       MultiAuthentication)
from moocng.api.authorization import (PublicReadTeachersModifyAuthorization,
                                      TeacherAuthorization,
                                      UserResourceAuthorization)
from moocng.api.mongodb import (MongoObj, MongoResource, MongoUserResource,
                                mongo_object_updated, mongo_object_created)
from moocng.api.tasks import (on_activity_created_task, on_answer_created_task,
                              on_answer_updated_task,
                              on_peerreviewsubmission_created_task)
from moocng.api.validation import (AnswerValidation, answer_validate_date,
                                   PeerReviewSubmissionsResourceValidation)
from moocng.assets.models import Asset, Reservation, AssetAvailability
from moocng.assets.utils import get_occupation_for_month
from moocng.courses.models import (Unit, KnowledgeQuantum, Question, Option,
                                   Attachment, Course)
from moocng.courses.marks import normalize_kq_weight, calculate_course_mark
from moocng.media_contents import (media_content_get_iframe_template,
                                   media_content_get_thumbnail_url)
from moocng.mongodb import get_db
from moocng.peerreview.models import PeerReviewAssignment, EvaluationCriterion
from moocng.peerreview.utils import (kq_get_peer_review_score,
                                     get_peer_review_review_score)


STATS_QUEUE = 'stats'


class HandleErrorProvider(object):

    def wrap_view(self, view):
        """
        Wraps methods so they can be called in a more functional way as well
        as handling exceptions better.
        """
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            response_class_error = None
            message_error = None
            message_error_default = _('Sorry, this request could not be processed. Please try again later.')
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                if request.is_ajax():
                    # IE excessively caches XMLHttpRequests, so we're disabling
                    # the browser cache here.
                    # See http://www.enhanceie.com/ie/bugs.asp for details.
                    patch_cache_control(response, no_cache=True)

                return response
            except (BadRequest, fields.ApiFieldError), e:
                response_class_error = http.HttpBadRequest
            except ValidationError, e:
                response_class_error = http.HttpBadRequest
                message_error = ', '.join(e.messages)
            except (NotFound, ObjectDoesNotExist), e:
                response_class_error = HttpResponseNotFound
            except Exception, e:
                # This exception could be an error with sensitive information
                message_error = message_error_default
            if hasattr(e, 'response'):
                return e.response
            if message_error is None:
                message_error = e.message
                if not message_error:
                    message_error = message_error_default
            if response_class_error is None:
                response_class_error = http.HttpApplicationError
            data = {
                "error_message": message_error,
            }
            if response_class_error != HttpResponseNotFound:
                #log = logging.getLogger('moocng.api.resources')
                logging.error('Internal Server Error: %s' % request.path, exc_info=sys.exc_info(),
                          extra={'status_code': 500, 'request': request})
            desired_format = self.determine_format(request)
            serialized = self.serialize(request, data, desired_format)
            return response_class_error(content=serialized, content_type=build_content_type(desired_format))

        return wrapper


class BaseResource(Resource, HandleErrorProvider):

    def wrap_view(self, view):
        return HandleErrorProvider.wrap_view(self, view)


class BaseModelResource(ModelResource, HandleErrorProvider):

    def wrap_view(self, view):
        return HandleErrorProvider.wrap_view(self, view)


class BaseMongoResource(MongoResource, HandleErrorProvider):

    def wrap_view(self, view):
        return HandleErrorProvider.wrap_view(self, view)


class BaseMongoUserResource(MongoUserResource, HandleErrorProvider):

    def wrap_view(self, view):
        return HandleErrorProvider.wrap_view(self, view)


class CourseResource(BaseModelResource):
    unit = fields.ToManyField('moocng.api.resources.UnitResource', 'unit_set')

    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        allowed_methods = ['get']
        excludes = ['certification_banner']
        authentication = MultiAuthentication(DjangoAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DjangoAuthorization()


class UnitResource(BaseModelResource):
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


class KnowledgeQuantumResource(BaseModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.ToManyField('moocng.api.resources.QuestionResource',
                                  'question_set', related_name='kq',
                                  readonly=True, null=True)
    iframe_code = fields.CharField(readonly=True)
    thumbnail_url = fields.CharField(readonly=True)
    peer_review_assignment = fields.ToOneField(
        'moocng.api.resources.PeerReviewAssignmentResource',
        'peerreviewassignment',
        related_name='peer_review_assignment',
        readonly=True, null=True)
    asset_availability = fields.ToOneField(
        'moocng.api.resources.AssetAvailabilityResource',
        'asset_availability',
        related_name='asset_availability',
        readonly=True, null=True)
    peer_review_score = fields.IntegerField(readonly=True)
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
        self.answers = db.get_collection('answers')
        self.activity = db.get_collection('activity')
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

    def dehydrate_iframe_code(self, bundle):
        return media_content_get_iframe_template(bundle.obj.media_content_type,
                                                 bundle.obj.media_content_id)

    def dehydrate_thumbnail_url(self, bundle):
        return media_content_get_thumbnail_url(bundle.obj.media_content_type,
                                               bundle.obj.media_content_id)

    def dehydrate_peer_review_score(self, bundle):
        return kq_get_peer_review_score(bundle.obj, bundle.request.user)

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

            answer = self.answers.find_one({
                "user_id": bundle.request.user.id,
                "question_id": question.id
            })
            if not answer:
                return False

            return question.is_correct(answer)

    def dehydrate_completed(self, bundle):
        return bundle.obj.is_completed(bundle.request.user)

    def dehydrate_course(self, bundle):
        return bundle.obj.unit.course.id

    def build_filters(self, filters=None):
        if filters is None: #if you don't pass any filters at all
            filters = {}
            
        orm_filters = super(KnowledgeQuantumResource, self).build_filters(filters)
        if('course' in filters):
            query = filters['course']
            qset = (
               Q(unit__course__id=query)
            )
            orm_filters['course'] = qset
            
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'course' in applicable_filters:
            course = applicable_filters.pop('course')
        else:
            course = None
        semi_filtered = super(KnowledgeQuantumResource, self).apply_filters(request, applicable_filters)
        return semi_filtered.filter(course) if course else semi_filtered

class PrivateKnowledgeQuantumResource(BaseModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.ToManyField('moocng.api.resources.QuestionResource',
                                  'question_set', related_name='kq',
                                  readonly=True, null=True)
    iframe_code = fields.CharField(readonly=True)
    thumbnail_url = fields.CharField(readonly=True)
    peer_review_assignment = fields.ToOneField(
        'moocng.api.resources.PeerReviewAssignmentResource',
        'peerreviewassignment',
        related_name='peer_review_assignment',
        readonly=True, null=True)
    asset_availability = fields.ToOneField(
        'moocng.api.resources.AssetAvailabilityResource',
        'asset_availability',
        related_name='asset_availability',
        readonly=True, null=True)
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

    def dehydrate_iframe_code(self, bundle):
        return media_content_get_iframe_template(bundle.obj.media_content_type, bundle.obj.media_content_id)

    def dehydrate_thumbnail_url(self, bundle):
        return media_content_get_thumbnail_url(bundle.obj.media_content_type, bundle.obj.media_content_id)


class AttachmentResource(BaseModelResource):
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


class PeerReviewAssignmentResource(BaseModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = PeerReviewAssignment.objects.all()
        resource_name = 'peer_review_assignment'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
            "unit": ('exact'),
        }

    def get_object_list(self, request):
        objects = super(PeerReviewAssignmentResource, self).get_object_list(request)

        unit = request.GET.get('unit', None)
        if unit is not None:
            objects = objects.filter(kq__unit_id=unit)

        return objects.filter(
            Q(kq__unit__unittype='n') |
            Q(kq__unit__start__isnull=True) |
            Q(kq__unit__start__isnull=False, kq__unit__start__lte=datetime.now)
        )


class PrivatePeerReviewAssignmentResource(BaseModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = PeerReviewAssignment.objects.all()
        resource_name = 'privpeer_review_assignment'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "kq": ('exact'),
        }


class EvaluationCriterionResource(BaseModelResource):
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
            Q(assignment__kq__unit__start__isnull=False,
              assignment__kq__unit__start__lte=datetime.now)
        )


class PrivateEvaluationCriterionResource(BaseModelResource):
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


class PeerReviewSubmissionsResource(BaseMongoResource):
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
        from moocng.peerreview.utils import insert_p2p_if_does_not_exists_or_raise
        _id = insert_p2p_if_does_not_exists_or_raise(bundle.data, self._collection)

        bundle.obj = MongoObj(bundle.data)
        self.send_created_signal(request.user.id, bundle.obj)
        bundle.obj.uuid = str(_id)

        bundle.uuid = bundle.obj.uuid

        return bundle


class PeerReviewReviewsResource(BaseMongoResource):
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


class QuestionResource(BaseModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')
    iframe_code = fields.CharField(readonly=True)
    thumbnail_url = fields.CharField(readonly=True)

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

    def dehydrate_solution_media_content_type(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if (unit.unittype != 'n' and
                unit.deadline > datetime.now(unit.deadline.tzinfo)):
            return None
        return bundle.obj.solution_media_content_type

    def dehydrate_solution_media_content_id(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if (unit.unittype != 'n' and
                unit.deadline > datetime.now(unit.deadline.tzinfo)):
            return None
        return bundle.obj.solution_media_content_id

    def dehydrate_solution_text(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if (unit.unittype != 'n' and
                unit.deadline > datetime.now(unit.deadline.tzinfo)):
            return None
        return bundle.obj.solution_text

    def dehydrate_last_frame(self, bundle):
        try:
            return bundle.obj.last_frame.url
        except ValueError:
            return "%simg/no-image.png" % settings.STATIC_URL

    def dehydrate_iframe_code(self, bundle):
        return media_content_get_iframe_template(
            bundle.obj.solution_media_content_type,
            bundle.obj.solution_media_content_id
        )

    def dehydrate_thumbnail_url(self, bundle):
        return media_content_get_thumbnail_url(
            bundle.obj.solution_media_content_type,
            bundle.obj.solution_media_content_id
        )


class PrivateQuestionResource(BaseModelResource):
    kq = fields.ToOneField(PrivateKnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'privquestion'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        always_return_data = True
        filtering = {
            "kq": ('exact'),
        }

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


class OptionResource(BaseModelResource):
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
            Q(question__kq__unit__start__isnull=False,
              question__kq__unit__start__lte=datetime.now)
        )

    def dispatch(self, request_type, request, **kwargs):
        # We need the request to dehydrate some fields
        try:
            question_id = int(request.GET.get("question", None))
        except ValueError:
            raise BadRequest("question filter isn't a integer value")
        collection = get_db().get_collection('answers')
        self.answer = collection.find_one({
            "user_id": request.user.id,
            "question_id": question_id
        })
        return super(OptionResource, self).dispatch(request_type, request,
                                                    **kwargs)

    def dehydrate_solution(self, bundle):
        # Only return the solution if the user has given an answer
        # If there is a deadline, then only return the solution if the deadline
        # has been reached too
        if self.answer:
            unit = bundle.obj.question.kq.unit
            if (unit.unittype == 'n' or
                not(unit.deadline and
                    datetime.now(unit.deadline.tzinfo) > unit.deadline)):
                return bundle.obj.solution

    def dehydrate_feedback(self, bundle):
        # Only return the feedback if the user has given an answer
        if self.answer:
            return bundle.obj.feedback


class AnswerResource(BaseMongoUserResource):

    course_id = fields.IntegerField(null=False)
    unit_id = fields.IntegerField(null=False)
    kq_id = fields.IntegerField(null=False)
    question_id = fields.IntegerField(null=False)
    date = fields.DateTimeField(readonly=True, default=datetime.now)
    replyList = fields.ListField(null=False)

    class Meta:
        resource_name = 'answer'
        collection = 'answers'
        datakey = 'question_id'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "question_id": ('exact'),
            "course_id": ('exact'),
            "unit_id": ('exact'),
            "kq_id": ('exact'),
        }
        validation = AnswerValidation()
        input_schema = {
            "course_id": 1,
            "unit_id": 1,
            "kq_id": 1,
            "question_id": 1,
            "replyList": 1,
            "user_id": 0,
            "date": 0,
        }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data["date"] = datetime.utcnow()
        bundle = super(AnswerResource, self).obj_create(bundle, request)
        bundle.uuid = bundle.obj.question_id
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):

        answer_validate_date(bundle, request)
        question_id = int(kwargs.get("pk"))
        if (len(bundle.data.get("replyList", [])) > 0):
            newobj = self._collection.find_and_modify({
                'user_id': request.user.id,
                'question_id': question_id,
            }, update={
                "$set": {
                    'replyList': bundle.data.get("replyList"),
                    "date": datetime.utcnow(),
                }
            }, safe=True, new=True)

        bundle.obj = newobj
        self.send_updated_signal(request.user.id, bundle.obj)
        return bundle


class ActivityResource(BaseMongoUserResource):

    course_id = fields.IntegerField(null=False)
    unit_id = fields.IntegerField(null=False)
    kq_id = fields.IntegerField(null=False)

    class Meta:
        resource_name = 'activity'
        collection = 'activity'
        datakey = 'kq_id'
        object_class = MongoObj
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post']
        filtering = {
            "course_id": ('exact'),
            "unit_id": ('exact'),
            "kq_id": ('exact'),
        }
        input_schema = {
            "course_id": 1,
            "unit_id": 1,
            "kq_id": 1,
            "user_id": 1
        }

    def _initial(self, request, **kwargs):
        course_id = kwargs['pk']
        return {
            "course_id": course_id,
            "unit_id": -1,
            "kq_id": -1,
            "user_id": -1,
        }


class UserResource(BaseModelResource):

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
            'email': ('iexact')
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
                return User.objects.get(email__iexact=kwargs['pk'])
            else:
                return self.cached_obj_get(request=request,
                                           **self.remove_api_resource_names(kwargs))
        except self.Meta.object_class.DoesNotExist:
            raise NotFound('User does not exist')

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
        # In tastypie, the override_urls don't call
        # Authentication/Authorization
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


class AssetResource(BaseModelResource):
    available_in = fields.ToManyField('moocng.api.resources.AssetAvailabilityResource', 'available_in')

    class Meta:
        queryset = Asset.objects.all()
        resource_name = 'asset'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "available_in": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):

        availability = request.GET.get('availability', None)
        kq = request.GET.get('kq', None)
        exclude_kq = request.GET.get('exclude_kq', None)
        course = request.GET.get('course', None)

        if availability is not None:
            results = Asset.objects.filter(available_in__id=availability)
        elif kq is not None:
            results = Asset.objects.filter(available_in__kq__id=kq)
        elif exclude_kq is not None:
            results = Asset.objects.exclude(available_in__kq__id=exclude_kq)
        elif course is not None:
            results = Asset.objects.filter(available_in__kq__unit__course__id=course)
        else:
            results = Asset.objects.all()
        return results


class PrivateAssetResource(BaseModelResource):
    available_in = fields.ToManyField('moocng.api.resources.AssetAvailabilityResource', 'available_in')

    class Meta:
        queryset = Asset.objects.all()
        resource_name = 'privasset'
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "available_in": ('exact'),
        }

    def obj_get_list(self, request=None, **kwargs):

        availability = request.GET.get('availability', None)
        kq = request.GET.get('kq', None)
        exclude_kq = request.GET.get('exclude_kq', None)
        course = request.GET.get('course', None)

        if availability is not None:
            results = Asset.objects.filter(available_in__id=availability)
        elif kq is not None:
            results = Asset.objects.filter(available_in__kq__id=kq)
        elif exclude_kq is not None:
            results = Asset.objects.exclude(available_in__kq__id=exclude_kq)
        elif course is not None:
            results = Asset.objects.filter(available_in__kq__unit__course__id=course)

        else:
            results = Asset.objects.all()
        return results


class AssetAvailabilityResource(BaseModelResource):

    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')
    assets = fields.ToManyField(AssetResource, 'assets')
    can_be_booked = fields.BooleanField(readonly=True)

    max_reservations_pending = fields.IntegerField(readonly=True)
    max_reservations_total = fields.IntegerField(readonly=True)

    class Meta:
        queryset = AssetAvailability.objects.all()
        resource_name = 'asset_availability'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
            "assets": ('exact'),
        }

    def dehydrate_max_reservations_pending(self, bundle):
        return bundle.obj.kq.unit.course.max_reservations_pending

    def dehydrate_max_reservations_total(self, bundle):
        return bundle.obj.kq.unit.course.max_reservations_total

    def dehydrate_can_be_booked(self, bundle):
        if bundle.obj.available_to < date.today():
            return False
        else:
            return True

    def obj_get_list(self, request=None, **kwargs):

        kq = request.GET.get('kq', None)
        asset = request.GET.get('asset', None)

        if kq is not None and asset is not None:
            results = AssetAvailability.objects.filter(Q(kq__id=kq) & Q(assets__available_in__id=asset))
        elif kq is not None:
            results = AssetAvailability.objects.filter(kq__id=kq)
        elif asset is not None:
            results = AssetAvailability.objects.filter(assets__available_in__id=asset)
        else:
            results = AssetAvailability.objects.all()
        return results


class PrivateAssetAvailabilityResource(BaseModelResource):

    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')
    assets = fields.ToManyField(AssetResource, 'assets')
    can_be_booked = fields.BooleanField(readonly=True)

    max_reservations_pending = fields.IntegerField(readonly=True)
    max_reservations_total = fields.IntegerField(readonly=True)

    class Meta:
        queryset = AssetAvailability.objects.all()
        resource_name = 'privasset_availability'
        always_return_data = True
        authentication = TeacherAuthentication()
        authorization = TeacherAuthorization()
        filtering = {
            "kq": ('exact'),
            "assets": ('exact'),
        }

    def dehydrate_max_reservations_pending(self, bundle):
        return bundle.obj.kq.unit.course.max_reservations_pending

    def dehydrate_max_reservations_total(self, bundle):
        return bundle.obj.kq.unit.course.max_reservations_total

    def dehydrate_can_be_booked(self, bundle):
        if isinstance(bundle.obj.available_to, datetime):
            bundle.obj.available_to = bundle.obj.available_to.date()
        if bundle.obj.available_to < date.today():
            return False
        else:
            return True

    def obj_get_list(self, request=None, **kwargs):

        kq = request.GET.get('kq', None)
        asset = request.GET.get('asset', None)

        if kq is not None and asset is not None:
            results = AssetAvailability.objects.filter(Q(kq__id=kq) & Q(assets__available_in__id=asset))
        elif kq is not None:
            results = AssetAvailability.objects.filter(kq__id=kq)
        elif asset is not None:
            results = AssetAvailability.objects.filter(assets__available_in__id=asset)
        else:
            results = AssetAvailability.objects.all()
        return results


class ReservationResource(BaseModelResource):
    user = fields.ToOneField(UserResource, 'user')
    asset = fields.ToOneField(AssetResource, 'asset')
    reserved_from = fields.ToOneField(AssetAvailabilityResource, 'reserved_from')
    remaining_time = fields.IntegerField(readonly=True)
    active_in = fields.IntegerField(readonly=True)

    class Meta:
        queryset = Reservation.objects.all()
        resource_name = 'reservation'
        allowed_methods = ['get']
        authentication = MultiAuthentication(DjangoAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DjangoAuthorization()
        filtering = {
            "asset": ('exact'),
            "user": ('exact'),
            "reserved_from": ('exact'),
        }

    def dehydrate_active_in(self, bundle):
        reservation_begins = bundle.obj.reservation_begins.replace(tzinfo=None)
        dif = (reservation_begins - datetime.utcnow())
        return dif.seconds + dif.days * 86400

    def dehydrate_remaining_time(self, bundle):
        reservation_begins = bundle.obj.reservation_begins.replace(tzinfo=None)
        reservation_ends = bundle.obj.reservation_ends.replace(tzinfo=None)
        now = max(datetime.utcnow(), reservation_begins)
        dif = (reservation_ends - now)
        return dif.seconds + dif.days * 86400

    def obj_get_list(self, request=None, **kwargs):

        asset = request.GET.get('asset', None)
        user = request.GET.get('user', None)
        kq = request.GET.get('kq', None)

        results = Reservation.objects.all()

        if asset is not None:
            results = results.filter(asset__id=asset)

        if user is not None:
            results = results.filter(user__id=user)

        if kq is not None:
            results = results.filter(reserved_from__kq=kq)

        return results


class ReservationCount(BaseResource):
    count = fields.IntegerField(readonly=True)
    reservation_begins = fields.DateTimeField(readonly=True)

    class Meta:
        resource_name = 'reservation_count'
        allowed_methods = 'get'

    def dehydrate_count(self, bundle):
        return bundle.obj['reservation_begins__count']

    def dehydrate_reservation_begins(self, bundle):
        base_date = bundle.obj['reservation_begins']
        return timezone.localtime(base_date, timezone.get_default_timezone())

    def obj_get(self, request, **kwargs):
        #Information can only be obtained if asking for a list
        return {'reservation_begins': '', 'reservation_begins__count': ''}

    def obj_get_list(self, request, **kwargs):
        asset_id = request.GET.get('asset', None)
        ret = Reservation.objects.filter(asset__id=asset_id)

        try:
            date = datetime.strptime(request.GET.get('date', None), '%Y-%m-%d')
            ret = ret.filter(Q(reservation_begins__gte=date) &
                             Q(reservation_begins__lt=(date + timedelta(1))))
        except:
            return []

        ret = ret.values('reservation_begins').order_by('reservation_begins')
        ret = ret.annotate(Count('reservation_begins'))
        return ret


class OccupationInformation(BaseResource):
    day = fields.IntegerField(readonly=True)
    occupation = fields.DecimalField(readonly=True)

    class Meta:
        resource_name = 'occupation_information'
        allowed_methods = 'get'

    def dehydrate_day(self, bundle):
        return int(bundle.obj[0])

    def dehydrate_occupation(self, bundle):
        return bundle.obj[1]

    def obj_get(self, request, **kwargs):
        #Information can only be obtained if asking for a list
        return {'day': '', 'occupation': ''}

    def obj_get_list(self, request, **kwargs):
        try:
            asset_id = int(request.GET.get('asset', ''))
            month = int(request.GET.get('month', ''))
            year = int(request.GET.get('year', ''))
        except ValueError:
            return []

        ret = get_occupation_for_month(asset_id, month, year)
        return ret


api_task_logger = logging.getLogger("api_tasks")


def on_activity_created(sender, user_id, mongo_object, **kwargs):
    api_task_logger.debug("activity created")

    data = mongo_object.to_dict()
    activity = get_db().get_collection('activity')
    unit_activity = activity.find({
        'user_id': data['user_id'],
        'unit_id': data['unit_id'],
    }).count()
    course_activity = activity.find({
        'user_id': data['user_id'],
        'course_id': data['course_id']
    }).count()

    on_activity_created_task.apply_async(
        args=[data, unit_activity, course_activity],
        queue=STATS_QUEUE,
    )


def on_answer_created(sender, user_id, mongo_object, **kwargs):
    api_task_logger.debug("answer created")

    on_answer_created_task.apply_async(
        args=[mongo_object.to_dict()],
        queue=STATS_QUEUE,
    )


def on_answer_updated(sender, user_id, mongo_object, **kwargs):
    api_task_logger.debug("answer updated")

    on_answer_updated_task.apply_async(
        args=[mongo_object],  # it is already a dict
        queue=STATS_QUEUE,
    )


def on_peerreviewsubmission_created(sender, user_id, mongo_object, **kwargs):
    api_task_logger.debug("peer review submission created")

    on_peerreviewsubmission_created_task.apply_async(
        args=[mongo_object.to_dict()],
        queue=STATS_QUEUE,
    )


mongo_object_created.connect(on_activity_created, sender=ActivityResource,
                             dispatch_uid="activity_created")
mongo_object_created.connect(on_answer_created, sender=AnswerResource,
                             dispatch_uid="answer_created")
mongo_object_updated.connect(on_answer_updated, sender=AnswerResource,
                             dispatch_uid="answer_updated")
mongo_object_created.connect(on_peerreviewsubmission_created,
                             sender=PeerReviewSubmissionsResource,
                             dispatch_uid="peerreviewsubmission_created")
