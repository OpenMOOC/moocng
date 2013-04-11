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

from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound, BadRequest
from tastypie.resources import Resource

from django.dispatch import Signal

from moocng.mongodb import get_db


mongo_object_created = Signal(providing_args=["user_id", "obj"])


def validate_dict_schema(obj, schema):
    for (key, value) in obj.items():
        if key not in schema:
            raise BadRequest("%s is not in resource schema" % key)

    for (key, value) in schema.items():
        if value == 1 and key not in obj:
            return BadRequest("%s required field %s is not in data provide" % key)

    return True


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
    mongo_schema = None

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

    def get_object_list(self, request, filter=None):
        results = []
        if filter is None:
            filter = {}

        for result in self._collection.find(filter):
            obj = MongoObj(initial=result)
            obj.uuid = str(result['_id'])
            results.append(obj)

        return results

    def obj_get_list(self, request=None, **kwargs):
        # no filtering by now
        return self.get_object_list(request, kwargs)

    def obj_get(self, request=None, **kwargs):

        result = self._collection.find(kwargs)
        if result.count() == 0:
            raise NotFound('Invalid resource lookup data provided')
        elif result.count() > 1:
            raise NotFound('Dulicate resource')

        obj = MongoObj(initial=result[0])
        obj.uuid = str(result[0]['_id'])
        return obj

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = self.full_hydrate(bundle)
        self.validate_schema(bundle)
        bundle.obj = MongoObj(bundle.data)
        _id = self._collection.insert(bundle.data, safe=True)
        mongo_object_created.send_robust(sender=self, mongo_object=bundle.data)
        bundle.obj.uuid = str(_id)
        return bundle

    def dehydrate(self, bundle):
        bundle.data.update(bundle.obj.to_dict())
        return bundle

    def _initial(self, request, **kwargs):
        return {}

    def validate_schema(self, bundle):
        if self.mongo_schema:
            validate_dict_schema(bundle.data, self.mongo_schema)


class MongoUserResource(MongoResource):
    """MongoResource with basic operations logged user relate"""

    user_id_field = "user_id"

    def get_object_list(self, request, filter=None):
        if not isinstance(filter, dict):
            filter = {}
        filter[self.user_id_field] = request.user.id

        return super(MongoUserResource, self).get_object_list(request, filter)

    def obj_get(self, request=None, **kwargs):

        if not isinstance(kwargs, dict):
            kwargs = {}
        kwargs[self.user_id_field] = request.user.id

        return super(MongoUserResource, self).obj_get(request, **kwargs)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data[self.user_id_field] = request.user.id
        return super(MongoUserResource, self).obj_create(bundle, request, **kwargs)
