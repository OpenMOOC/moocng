# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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

from moocng.api.tests.outputs import API_DESCRIPTION
from moocng.api.tests.utils import ApiTestCase


class ServicesTestCase(ApiTestCase):

    def test_api_description(self):
        response = self.client.get('/api/%s/%s' % (self.api_name, self.format_append))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, API_DESCRIPTION)
