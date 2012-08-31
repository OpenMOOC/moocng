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

import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from pymongo.connection import Connection

from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource

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
            port=self.db_uri.port or DEFAULT_MONGODB_PORT)

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


def get_db():
    try:
        db_uri = settings.MONGODB_URI
    except AttributeError:
        raise ImproperlyConfigured('Missing required MONGODB_URI setting')

    return MongoDB(db_uri)


def get_user(request, collection):
    return collection.find_one({'user': request.user.id}, safe=True)


def get_or_create_user(request, collection, key, initial):
    user_id = request.user.id

    user = collection.find_one({'user': user_id}, safe=True)
    if user is None:
        user = {'user': user_id, key: initial}
        user['_id'] = collection.insert(user)

    return user


class MongoObj(object):
    """This class is required for Tastypie"""

    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class MongoResource(Resource):

    collection = None  # subclasses should implement this

    def __init__(self, *args, **kwargs):
        super(MongoResource, self).__init__(*args, **kwargs)

        self._collection = get_db().get_collection(self._meta.collection)

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {'resource_name': self._meta.resource_name}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = str(bundle_or_obj.obj.uuid)
        else:
            kwargs['pk'] = str(bundle_or_obj.uuid)

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request):
        results = []
        for result in self._collection.find():
            obj = MongoObj(initial=result)
            obj.uuid = str(result['_id'])
            results.append(obj)

        return results

    def obj_get_list(self, request=None, **kwargs):
        # no filtering by now
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        user = self._get_or_create_user(request, **kwargs)
        oid = kwargs['pk']

        result = user[self._meta.datakey].get(oid, None)
        if result is None:
            raise NotFound('Invalid resource lookup data provided')

        obj = MongoObj(initial=result)
        obj.uuid = oid
        return obj

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = self.full_hydrate(bundle)
        bundle.obj = MongoObj(bundle.data)
        _id = self._collection.insert(bundle.data, safe=True)
        bundle.obj.uuid = str(_id)
        return bundle

    def _get_or_create_user(self, request, **kwargs):
        return get_or_create_user(request, self._collection,
                                  self._meta.datakey,
                                  self._initial(request, **kwargs))

    def _initial(self, request, **kwargs):
        return {}
