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

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from moocng.api.models import UserApi
from moocng.mongodb import get_db
from moocng.courses.models import Course, Unit, KnowledgeQuantum, CourseTeacher


@override_settings(MONGODB_URI='mongodb://localhost:27017/moocng_test')
class ApiTestCase(TestCase):

    api_name = 'v1'
    format_append = '?format=json'
    up_collections = ('answers', 'activity')
    down_collections = ('answers', 'activity')

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.mongodb = get_db()
        for collection in self.up_collections:
            self.mongodb.database.drop_collection(collection)
            self.mongodb.database.create_collection(collection)

    def tearDown(self):
        super(ApiTestCase, self).tearDown()
        for collection in self.down_collections:
            self.mongodb.database.drop_collection(collection)

    def create_test_user_admin(self):
        return User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')

    def create_test_user_teacher1(self):
        return User.objects.create_user('teacher1', 'teacher1@example.com', 'teacher1123456')

    def create_test_user_teacher2(self):
        return User.objects.create_user('teacher2', 'teacher2@example.com', 'teacher2123456')

    def create_test_user_alum1(self):
        return User.objects.create_user('alum1', 'alum1@example.com', 'alum1123456')

    def create_test_user_alum2(self):
        return User.objects.create_user('alum2', 'alum2@example.com', 'alum2123456')

    def create_test_user_owner(self):
        return User.objects.create_user('owner', 'owner@example.com', 'owner123456')

    def create_test_user_user(self):
        return User.objects.create_user('user', 'user@example.com', 'user123456')

    def create_test_user_test(self):
        return User.objects.create_user('test', 'test@example.com', 'test123456')

    def django_login_user(self, client, user):
        client.login(username=user.username, password='%s123456' % (user.username))
        return client

    def generate_apikeyuser(self, user, key):
        apikeyuser = UserApi.objects.create(user=user, key=key)
        return apikeyuser

    def create_test_basic_course(self, owner, teacher=None, student=None, name=None):
        if not name:
            name = 'test_basic'
        test_course = Course(name='%s_course' % name,
                             slug='%s_course' % name,
                             description='%s_description' % name,
                             owner=owner)
        test_course.save()

        # A owner is a teacher
        CourseTeacher.objects.create(course=test_course, teacher=owner)

        if teacher:
            CourseTeacher.objects.create(course=test_course, teacher=teacher)
        if student:
            test_course.students.add(student)
        test_course.save()
        return test_course

    def create_test_basic_unit(self, course, unittype='n', start=None, deadline=None, weight=None):
        test_unit = Unit(title='test_basic_unit',
                         course=course,
                         unittype=unittype)
        if start:
            test_unit.start = start
        if deadline:
            test_unit.deadline = deadline
        if weight:
            test_unit.weight = weight
        test_unit.save()
        return test_unit

    def update_test_unit(self, test_unit, unittype='n', start=None, deadline=None, weight=None):
        test_unit.unittype = unittype
        if start:
            test_unit.start = start
        if deadline:
            test_unit.deadline = deadline
        if weight:
            test_unit.weight = weight

        test_unit.save()
        return test_unit

    def create_test_basic_kq(self, unit, video='http://www.youtube.com/watch?v=eW3gMGqcZQc', weight=0):
        test_kq = KnowledgeQuantum.objects.create(title='test_basic_kq',
                                unit=unit,
                                video=video,
                                weight=weight)
        return test_kq

    def create_activity(self, user, kq):
        key = 'courses'
        course_id = str(kq.unit.course.id)
        activity_collection = get_db().get_collection('activity')
        user_data = activity_collection.find_one({'user': user.id}, safe=True)
        if user_data is None or not (key in user_data or course_id in user_data[key]):
            initial = {course_id: {'kqs': []}}
            user_data = {'user': user.id, key: initial}
            user_data['_id'] = activity_collection.insert(user_data)
            user_data[key][course_id]['kqs'] = [str(kq.id)]
        else:
            user_data[key][course_id]['kqs'].append(str(kq.id))

        activity_collection.update({'_id': user_data['_id']}, user_data)
