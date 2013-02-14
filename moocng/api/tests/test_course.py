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

from django.utils import simplejson

from moocng.api.tests.utils import ApiTestCase
from moocng.api.tests.outputs import (NO_OBJECTS, BASIC_COURSES, BASIC_COURSE)


class CoursesTestCase(ApiTestCase):

    def test_get_courses_annonymous(self):
        # TODO: Check not published course

        owner = self.create_test_user_owner()

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner)
        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner, student=alum1)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner, teacher=teacher1)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)

    def test_get_courses_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSES)


class CourseTestCase(ApiTestCase):

    # Get course
    def test_get_course_annonymous(self):
        owner = self.create_test_user_owner()

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)
        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner, student=alum1)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner, teacher=teacher1)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    def test_get_course_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_COURSE)

    # Change course_slug
    def test_change_slug_annonymous(self):
        pass

    def test_change_slug_user(self):
        pass

    def test_change_slug_alum(self):
        pass

    def test_change_slug_teacher(self):
        pass

    def test_change_slug_owner(self):
        pass

    def test_change_slug_admin(self):
        pass

    # Create course
    def test_create_course_annonymous(self):
        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course_user(self):
        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course_alum(self):
        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course_teacher(self):
        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course__admin(self):
        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_create_course_certificator(self):
        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        response = self.client.post('/api/%s/course/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    # Update course
    def test_put_course_annonymous(self):
        owner = self.create_test_user_owner()

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        self.create_test_basic_course(owner)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        self.create_test_basic_course(owner, student=alum1)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        self.create_test_basic_course(owner, teacher=teacher1)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        self.create_test_basic_course(owner)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        self.create_test_basic_course(owner)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_put_course_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        self.create_test_basic_course(owner)

        response = self.client.put('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    # Delete course
    def test_delete_course_annonymous(self):
        owner = self.create_test_user_owner()

        response = self.client.get('/api/%s/course/1/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_basic_course(owner)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        self.create_test_basic_course(owner)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        self.create_test_basic_course(owner, student=alum1)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        self.create_test_basic_course(owner, teacher=teacher1)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        self.create_test_basic_course(owner)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        self.create_test_basic_course(owner)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)

    def test_delete_course_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        self.create_test_basic_course(owner)

        response = self.client.delete('/api/%s/course/1/%s' % (self.api_name, self.format_append), simplejson.loads(BASIC_COURSE))
        self.assertEqual(response.status_code, 405)
