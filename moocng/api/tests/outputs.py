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


API_DESCRIPTION = '{"activity": {"list_endpoint": "/api/v1/activity/", "schema": "/api/v1/activity/schema/"}, "answer": {"list_endpoint": "/api/v1/answer/", "schema": "/api/v1/answer/schema/"}, "attachment": {"list_endpoint": "/api/v1/attachment/", "schema": "/api/v1/attachment/schema/"}, "course": {"list_endpoint": "/api/v1/course/", "schema": "/api/v1/course/schema/"}, "kq": {"list_endpoint": "/api/v1/kq/", "schema": "/api/v1/kq/schema/"}, "option": {"list_endpoint": "/api/v1/option/", "schema": "/api/v1/option/schema/"}, "privkq": {"list_endpoint": "/api/v1/privkq/", "schema": "/api/v1/privkq/schema/"}, "privquestion": {"list_endpoint": "/api/v1/privquestion/", "schema": "/api/v1/privquestion/schema/"}, "question": {"list_endpoint": "/api/v1/question/", "schema": "/api/v1/question/schema/"}, "unit": {"list_endpoint": "/api/v1/unit/", "schema": "/api/v1/unit/schema/"}, "user": {"list_endpoint": "/api/v1/user/", "schema": "/api/v1/user/schema/"}}'

NO_OBJECTS = '{"meta": {"limit": 0, "offset": 0, "total_count": 0}, "objects": []}'

BASIC_COURSES = '{"meta": {"limit": 0, "offset": 0, "total_count": 1}, "objects": [{"certification_available": false, "description": "test_basic_description", "end_date": null, "enrollment_method": "free", "estimated_effort": "", "id": "1", "intended_audience": "", "learning_goals": "", "name": "test_basic_course", "order": 1, "owner": "/api/v1/user/1/", "promotion_video": "", "requirements": "", "resource_uri": "/api/v1/course/1/", "slug": "test_basic_course", "start_date": null, "threshold": null}]}'


BASIC_COURSE = '{"certification_available": false, "description": "test_basic_description", "end_date": null, "enrollment_method": "free", "estimated_effort": "", "id": "1", "intended_audience": "", "learning_goals": "", "name": "test_basic_course", "order": 1, "owner": "/api/v1/user/1/", "promotion_video": "", "requirements": "", "resource_uri": "/api/v1/course/1/", "slug": "test_basic_course", "start_date": null, "threshold": null}'

BASIC_UNITS = '{"meta": {"limit": 0, "offset": 0, "total_count": 1}, "objects": [{"course": "/api/v1/course/1/", "deadline": null, "id": "1", "order": 1, "resource_uri": "/api/v1/unit/1/", "start": null, "title": "test_basic_unit", "unittype": "n", "weight": 0}]}'

BASIC_UNIT = '{"course": "/api/v1/course/1/", "deadline": null, "id": "1", "order": 1, "resource_uri": "/api/v1/unit/1/", "start": null, "title": "test_basic_unit", "unittype": "n", "weight": 0}'

NORMAL_USER = '{"email": "test@example.com", "first_name": "", "id": "2", "last_name": "", "resource_uri": "/api/v1/user/2/"}'


BASIC_ALLCOURSES = '{"meta": {"limit": 0, "offset": 0, "total_count": 2}, "objects": [{"certification_available": false, "description": "course1_description", "end_date": null, "enrollment_method": "free", "estimated_effort": "", "id": "1", "intended_audience": "", "learning_goals": "", "name": "course1_course", "order": 1, "owner": "/api/v1/user/1/", "promotion_video": "", "requirements": "", "resource_uri": "/api/v1/course/1/", "slug": "course1_course", "start_date": null, "threshold": null}, {"certification_available": false, "description": "course2_description", "end_date": null, "enrollment_method": "free", "estimated_effort": "", "id": "2", "intended_audience": "", "learning_goals": "", "name": "course2_course", "order": 2, "owner": "/api/v1/user/1/", "promotion_video": "", "requirements": "", "resource_uri": "/api/v1/course/2/", "slug": "course2_course", "start_date": null, "threshold": null}]}'
