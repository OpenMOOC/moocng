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

import uuid

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from moocng.api.tests.utils import ApiTestCase
from moocng.api.tests.outputs import (NO_OBJECTS, NORMAL_USER,
                                      BASIC_ALLCOURSES)


class UserTestCase(ApiTestCase):

    # Get user
    def test_get_user_annonymous(self):
        self.create_test_user_user()

        self.create_test_user_test()

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

    def test_get_user_user(self):
        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

    def test_get_user_alum(self):
        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

    def test_get_user_teacher(self):
        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NORMAL_USER)

    def test_get_user_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NORMAL_USER)

    def test_get_user_admin(self):
        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 404)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NORMAL_USER)

    def test_get_user_userkey(self):
        user = self.create_test_user_user()

        key = str(uuid.uuid4())
        self.generate_apikeyuser(user, key)

        response = self.client.get('/api/%s/user/2/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 404)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 401)

    def test_get_user_certificator(self):
        certuser = self.create_test_user_user()

        key = str(uuid.uuid4())
        self.generate_apikeyuser(certuser, key)

        response = self.client.get('/api/%s/user/2/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 404)

        self.create_test_user_test()
        response = self.client.get('/api/%s/user/2/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NORMAL_USER)

    # Get courses of the user
    def test_get_allcourses_annonymous(self):
        owner = self.create_test_user_owner()

        self.create_test_user_user()

        test_user = self.create_test_user_test()

        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

    def test_get_allcourses_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        test_user = self.create_test_user_test()

        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

    def test_get_allcourses_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        test_user = self.create_test_user_test()

        course1 = self.create_test_basic_course(owner=owner,
                                                student=test_user,
                                                name='course1')
        course2 = self.create_test_basic_course(owner=owner,
                                                student=test_user,
                                                name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        course1.students.add(alum1)
        course1.save()
        course2.students.add(alum1)
        course2.save()

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_ALLCOURSES)

    def test_get_allcourses_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        test_user = self.create_test_user_test()

        self.create_test_basic_course(owner=owner,
                                      teacher=teacher1,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      teacher=teacher1,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

    def test_get_allcourses_owner(self):
        teacher1 = self.create_test_user_teacher1()

        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        test_user = self.create_test_user_test()

        self.create_test_basic_course(owner=owner,
                                      teacher=teacher1,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      teacher=teacher1,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

    def test_get_allcourses_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        test_user = self.create_test_user_test()

        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

    def test_get_allcourses_userkey(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()

        key = str(uuid.uuid4())
        self.generate_apikeyuser(user, key)

        test_user = self.create_test_user_test()

        response = self.client.get('/api/%s/user/3/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 401)

        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 401)

        response = self.client.get('/api/%s/user/2/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 401)

    def test_get_allcourses_certificator(self):
        owner = self.create_test_user_owner()

        certificator = self.create_test_user_user()

        ct = ContentType.objects.get(model='course', app_label='courses')
        perm = Permission.objects.get(content_type=ct, codename='can_list_allcourses')
        certificator.user_permissions.add(perm)

        key = str(uuid.uuid4())
        self.generate_apikeyuser(certificator, key)

        test_user = self.create_test_user_test()

        response = self.client.get('/api/%s/user/3/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)

        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course1')
        self.create_test_basic_course(owner=owner,
                                      student=test_user,
                                      name='course2')

        response = self.client.get('/api/%s/user/3/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BASIC_ALLCOURSES)

        response = self.client.get('/api/%s/user/2/allcourses/%s&key=%s' % (self.api_name, self.format_append, key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, NO_OBJECTS)
