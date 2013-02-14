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

from datetime import datetime, timedelta

from django.utils.timezone import utc
from django.utils import simplejson

from moocng.api.tests.utils import ApiTestCase

from moocng.api.tests.outputs import (NO_OBJECTS, BASIC_UNITS, BASIC_UNIT)


class UnitsTestCase(ApiTestCase):

    def test_get_units_annonymous(self):
        # TODO: Check not "public" course
        owner = self.create_test_user_owner()

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        # Test public course
        course = self.create_test_basic_course(owner, teacher=teacher1)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        # Test public course/
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)

    def test_get_units_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_units(course, is_possible=True)


    # Auxiliary function
    def check_test_get_units(self, course, is_possible=False):
        # Test units with no start, no deadline (only normal units)
        unit = self.create_test_basic_unit(course, 'n')
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, BASIC_UNITS)
        else:
            self.assertEqual(response.status_code, 401)

        now = datetime.utcnow().replace(tzinfo=utc)
        aux_basic_units = simplejson.loads(BASIC_UNITS)

        # Test units with start and deadline, referenced date before start
        # strftime('%Y-%m-%dT%H:%M:%S%z')
        start = now + timedelta(days=1)
        deadline = now + timedelta(days=2)
        
        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_units['objects'][0]['unittype'] = u'h'
        aux_basic_units['objects'][0]['start'] = unicode(start.isoformat())
        aux_basic_units['objects'][0]['deadline'] = unicode(deadline.isoformat())
        
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_units['objects'][0]['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)

        # Test units with start and deadline, referenced date between start, deadline
        start = now - timedelta(days=1)
        deadline = now + timedelta(days=1)

        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_units['objects'][0]['unittype'] = u'h'
        aux_basic_units['objects'][0]['start'] = unicode(start.isoformat())
        aux_basic_units['objects'][0]['deadline'] = unicode(deadline.isoformat())
        
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_units['objects'][0]['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)

        # Test units with start and deadline, referenced date after deadline
        start = now - timedelta(days=2) 
        deadline = now - timedelta(days=1) 

        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_units['objects'][0]['unittype'] = u'h'
        aux_basic_units['objects'][0]['start'] = unicode(start.isoformat())
        aux_basic_units['objects'][0]['deadline'] = unicode(deadline.isoformat())

        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_units['objects'][0]['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_units)
        else:
            self.assertEqual(response.status_code, 401)


class UnitTestCase(ApiTestCase):

    def test_get_unit_annonymous(self):
        # TODO: Check not "public" course
        owner = self.create_test_user_owner()

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_user(self):
        owner = self.create_test_user_owner()

        user = self.create_test_user_user()
        self.client = self.django_login_user(self.client, user)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_alum(self):
        owner = self.create_test_user_owner()

        alum1 = self.create_test_user_alum1()
        self.client = self.django_login_user(self.client, alum1)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_teacher(self):
        owner = self.create_test_user_owner()

        teacher1 = self.create_test_user_teacher1()
        self.client = self.django_login_user(self.client, teacher1)

        # Test public course
        course = self.create_test_basic_course(owner, teacher=teacher1)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_owner(self):
        owner = self.create_test_user_owner()
        self.client = self.django_login_user(self.client, owner)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_admin(self):
        owner = self.create_test_user_owner()

        admin = self.create_test_user_admin()
        self.client = self.django_login_user(self.client, admin)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    def test_get_unit_certificator(self):
        owner = self.create_test_user_owner()

        certuser = self.create_test_user_user()
        self.client = self.apikey_login_user(self.client, certuser)

        # Test public course
        course = self.create_test_basic_course(owner)
        self.check_test_get_unit(course, is_possible=True)

    # Auxiliary function
    def check_test_get_unit(self, course, is_possible=False):
        # Test unit with no start, no deadline (normal unit)
        unit = self.create_test_basic_unit(course, 'n')
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, BASIC_UNIT)
        else:
            self.assertEqual(response.status_code, 401)

        now = datetime.utcnow().replace(tzinfo=utc)
        aux_basic_unit = simplejson.loads(BASIC_UNIT)

        # Test unit with start and deadline, referenced date before start
        # strftime('%Y-%m-%dT%H:%M:%S%z')
        start = now + timedelta(days=1)
        deadline = now + timedelta(days=2)
        
        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_unit['unittype'] = u'h'
        aux_basic_unit['start'] = unicode(start.isoformat())
        aux_basic_unit['deadline'] = unicode(deadline.isoformat())
        
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_unit['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)

        # Test unit with start and deadline, referenced date between start, deadline
        start = now - timedelta(days=1)
        deadline = now + timedelta(days=1)

        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_unit['unittype'] = u'h'
        aux_basic_unit['start'] = unicode(start.isoformat())
        aux_basic_unit['deadline'] = unicode(deadline.isoformat())
        
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_unit['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)

        # Test unit with start and deadline, referenced date after deadline
        start = now - timedelta(days=2) 
        deadline = now - timedelta(days=1) 

        unit.unittype = 'h'
        unit.start = start
        unit.deadline = deadline
        unit.save()

        aux_basic_unit['unittype'] = u'h'
        aux_basic_unit['start'] = unicode(start.isoformat())
        aux_basic_unit['deadline'] = unicode(deadline.isoformat())

        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)

        unit.unittype = 'e'
        aux_basic_unit['unittype'] = u'e'
        unit.save()
 
        response = self.client.get('/api/%s/unit/1/%s' % (self.api_name, self.format_append))
        if is_possible:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(simplejson.loads(response.content), aux_basic_unit)
        else:
            self.assertEqual(response.status_code, 401)
