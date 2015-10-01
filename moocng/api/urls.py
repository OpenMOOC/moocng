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

from django.conf.urls import include, patterns, url

from tastypie.api import Api
from moocng.api import resources


v1_api = Api(api_name='v1')
v1_api.register(resources.LanguageResource())
v1_api.register(resources.UnitResource())
v1_api.register(resources.KnowledgeQuantumResource())
v1_api.register(resources.PrivateKnowledgeQuantumResource())
v1_api.register(resources.AttachmentResource())
v1_api.register(resources.TranscriptionResource())
v1_api.register(resources.QuestionResource())
v1_api.register(resources.PrivateQuestionResource())
v1_api.register(resources.OptionResource())
v1_api.register(resources.AnswerResource())
v1_api.register(resources.ActivityResource())
v1_api.register(resources.HistoryResource())
v1_api.register(resources.CourseResource())
v1_api.register(resources.UserResource())
v1_api.register(resources.PeerReviewAssignmentResource())
v1_api.register(resources.PrivatePeerReviewAssignmentResource())
v1_api.register(resources.EvaluationCriterionResource())
v1_api.register(resources.PrivateEvaluationCriterionResource())
v1_api.register(resources.PeerReviewSubmissionsResource())
v1_api.register(resources.PeerReviewReviewsResource())
v1_api.register(resources.AssetResource())
v1_api.register(resources.AssetAvailabilityResource())
v1_api.register(resources.ReservationResource())
v1_api.register(resources.PrivateAssetResource())
v1_api.register(resources.PrivateAssetAvailabilityResource())
v1_api.register(resources.ReservationCount())
v1_api.register(resources.OccupationInformation())

urlpatterns = patterns(
    '',
    url(r'', include(v1_api.urls))
)
