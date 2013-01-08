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

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from django.conf.urls import url
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse

from moocng.api.authentication import DjangoAuthentication
from moocng.api.authorization import ApiKeyAuthorization, is_api_key_authorized
from moocng.api.mongodb import get_db, get_user, MongoObj, MongoResource
from moocng.courses.models import (Unit, KnowledgeQuantum, Question, Option,
                                   Attachment, Course)
from moocng.courses.utils import normalize_kq_weight, calculate_course_mark
from moocng.videos.utils import extract_YT_video_id


class UnitResource(ModelResource):

    class Meta:
        queryset = Unit.objects.all()
        resource_name = 'unit'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()


class KnowledgeQuantumResource(ModelResource):
    unit = fields.ToOneField(UnitResource, 'unit')
    question = fields.RelatedField('moocng.api.resources.QuestionResource',
                                   'question_set')
    videoID = fields.CharField(readonly=True)
    correct = fields.BooleanField()
    completed = fields.BooleanField()
    normalized_weight = fields.IntegerField()

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
        if question.count() == 0:
            return None
        else:
            return "/api/v1/question/%d/" % question.all()[0].id
        # TODO improve url

    def dehydrate_videoID(self, bundle):
        return extract_YT_video_id(bundle.obj.video)

    def dehydrate_correct(self, bundle):
        questions = bundle.obj.question_set.all()
        if questions.count() == 0:
            # no question: a kq is correct if it is completed
            return self._is_completed(self.user_activity, bundle.obj)
        else:
            question = questions[0]  # there should be only one question
            if self.user_answers is None:
                return False

            answer = self.user_answers.get('questions', {}).get(unicode(question.id))
            if answer is None:
                return False

            return question.is_correct(answer)

    def dehydrate_completed(self, bundle):
        return self._is_completed(self.user_activity, bundle.obj)

    def _is_completed(self, activity, kq):
        course_id = kq.unit.course.id
        if activity is None:
            return False

        courses = activity.get('courses', None)
        if courses is None:
            return False

        visited = courses.get(unicode(course_id), None)
        if visited is None:
            return False

        kqs = visited.get('kqs', None)
        if kqs is None:
            return False

        return unicode(kq.id) in kqs


class AttachmentResource(ModelResource):
    kq = fields.ToOneField(KnowledgeQuantumResource, 'kq')

    class Meta:
        queryset = Attachment.objects.all()
        resource_name = 'attachment'
        allowed_methods = ['get']
        authentication = DjangoAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            "kq": ('exact'),
        }

    def dehydrate_attachment(self, bundle):
        return bundle.obj.attachment.url


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

    def dehydrate_solution(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if unit.unittype != 'n' and unit.deadline > datetime.now(unit.deadline.tzinfo):
            return None
        return bundle.obj.solution

    def dehydrate_solutionID(self, bundle):
        # Only return solution if the deadline has been reached, or there is
        # no deadline
        unit = bundle.obj.kq.unit
        if unit.unittype != 'n' and unit.deadline > datetime.now(unit.deadline.tzinfo):
            return None
        return extract_YT_video_id(bundle.obj.solution)

    def dehydrate_last_frame(self, bundle):
        return bundle.obj.last_frame.url


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


class CourseResource(ModelResource):
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        excludes = ['certification_banner']
        allowed_methods = ['get']


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = ApiKeyAuthorization()
        allowed_methods = ['get']
        fields = ['id', 'email']
        filtering = {
            'email': ('exact'),
        }

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

    @is_api_key_authorized
    def get_courses(self, request, **kwargs):
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj
        courses = obj.courses_as_student.all()
        return self.alt_get_list(request, courses)

    @is_api_key_authorized
    def get_passed_courses(self, request, **kwargs):
        obj = self.get_object(request, kwargs)
        if isinstance(obj, HttpResponse):
            return obj
        courses = obj.courses_as_student.all()
        passed_courses = []

        for course in courses:
            if course.threshold is not None:
                total_mark, units_info = calculate_course_mark(course,
                                                               request.user)
                if not float(course.threshold) < total_mark:
                    passed_courses.append(course)

        return self.alt_get_list(request, passed_courses)
