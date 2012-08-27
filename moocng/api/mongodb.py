import bson

import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from pymongo.connection import Connection

from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource


class MongoDB(object):

    def __init__(self, db_uri):

        uri_parts = urlparse.urlparse(db_uri)

        if uri_parts.path:
            database_name = uri_parts.path[1:]
        else:
            try:
                database_name = settings.MONGODB_NAME
            except AttributeError:
                raise ImproperlyConfigured('You did not supply the database name in MONGODB_URI neither in MONGODB_NAME')

        self.connection = Connection(db_uri)
        self.database = self.connection[database_name]

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
