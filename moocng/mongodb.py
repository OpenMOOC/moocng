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

import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from pymongo.connection import Connection

DEFAULT_MONGODB_HOST = 'localhost'
DEFAULT_MONGODB_PORT = 27017
DEFAULT_MONGODB_NAME = 'moocng'
DEFAULT_MONGODB_URI = 'mongodb://%s:%d/%s' % (DEFAULT_MONGODB_HOST,
                                              DEFAULT_MONGODB_PORT,
                                              DEFAULT_MONGODB_NAME)


class MongoDB(object):

    def __init__(self, db_uri=DEFAULT_MONGODB_URI,
                 connection_factory=Connection):
        self.db_uri = urlparse.urlparse(db_uri)
        self.connection = connection_factory(
            host=self.db_uri.hostname or DEFAULT_MONGODB_HOST,
            port=self.db_uri.port or DEFAULT_MONGODB_PORT,
            tz_aware=True)

        if self.db_uri.path:
            self.database_name = self.db_uri.path[1:]
        else:
            self.database_name = DEFAULT_MONGODB_NAME

        self.database = self.get_database()

    def get_connection(self):
        return self.connection

    def get_database(self):
        database = self.connection[self.database_name]
        if self.db_uri.username and self.db_uri.password:
            database.authenticate(self.db_uri.username, self.db_uri.password)

        return database

    def get_collection(self, collection):
        return self.database[collection]


# this is not a thread local because we want
# the server workers to reuse as many connections as possible
_mongodb_connection = None


def get_db(force_connect=False):
    global _mongodb_connection
    try:
        db_uri = settings.MONGODB_URI
    except AttributeError:
        raise ImproperlyConfigured('Missing required MONGODB_URI setting')

    if _mongodb_connection is None or force_connect:
        _mongodb_connection = MongoDB(db_uri)

    return _mongodb_connection

def get_micro_blog_db(force_connect=False):

    return get_db()
