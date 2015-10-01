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

from bson import ObjectId

from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound, BadRequest
from tastypie.resources import Resource

from django.dispatch import Signal

from moocng.mongodb import get_db


mongo_object_created = Signal(providing_args=["user_id", "mongo_object"])
mongo_object_updated = Signal(providing_args=["user_id", "mongo_object"])


def validate_dict_schema(obj, schema):
    for (key, value) in obj.items():
        if key not in schema:
            raise BadRequest("%s is not in resource schema" % key)

    for (key, value) in schema.items():
        if value == 1 and key not in obj:
            raise BadRequest("required field %s is not in data provide" % key)

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

    class Meta:
        input_schema = {}

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

    def get_object_list(self, request, **kwargs):
        results = []
        filters = kwargs.get("filters", {})
        if self._meta.filtering:
            for filter in self._meta.filtering.keys():
                filter_value = request.GET.get(filter, None)
                if not filter_value is None:
                    try:
                        filters[filter] = int(filter_value)
                    except ValueError:
                        filters[filter] = filter_value

        for result in self._collection.find(filters):
            obj = MongoObj(initial=result)
            obj.uuid = str(result['_id'])
            results.append(obj)

        return results

    def obj_get_list(self, request=None, **kwargs):
        return self.get_object_list(request, **kwargs)

    def obj_get(self, request=None, **kwargs):
        filter = kwargs.copy()
        if 'pk' in kwargs:
            if self._meta.datakey == '_id':
                filter["_id"] = ObjectId(kwargs["pk"])
            else:
                try:
                    filter[self._meta.datakey] = int(kwargs["pk"])
                except ValueError:
                    filter[self._meta.datakey] = kwargs["pk"]
            filter.pop("pk")

        result = self._collection.find(filter)
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

        query_discover = kwargs.get("query_discover", {})
        query_discover[self._meta.datakey] = getattr(bundle.obj,
                                                     self._meta.datakey)

        if self._collection.find_one(query_discover):
            raise BadRequest("This object already exists")

        _id = self._collection.insert(bundle.obj.to_dict(), safe=True)

        self.send_created_signal(request.user.id, bundle)
        bundle.obj.uuid = str(_id)
        return bundle

    def send_created_signal(self, user_id, obj, **kwargs):
        mongo_object_created.send(self.__class__, user_id=user_id,
                                  mongo_object=obj)

    def send_updated_signal(self, user_id, obj, **kwargs):
        mongo_object_updated.send(self.__class__, user_id=user_id,
                                  mongo_object=obj)

    def dehydrate(self, bundle):
        bundle.data.update(bundle.obj.to_dict())
        return bundle

    def _initial(self, request, **kwargs):
        return {}

    def validate_schema(self, bundle):
        schema = getattr(self._meta, "input_schema", {})
        if schema:
            validate_dict_schema(bundle.data, schema)


class MongoUserResource(MongoResource):
    """MongoResource with basic operations logged user relate"""

    user_id_field = "user_id"

    def get_object_list(self, request, **kwargs):
        filters = kwargs.get("filters", {})
        filters[self.user_id_field] = request.user.id

        return super(MongoUserResource, self).get_object_list(request,
                                                              filters=filters)

    def obj_get(self, request=None, **kwargs):
        if not isinstance(kwargs, dict):
            kwargs = {}
        kwargs[self.user_id_field] = request.user.id
        return super(MongoUserResource, self).obj_get(request, **kwargs)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data[self.user_id_field] = request.user.id

        query_discover = kwargs.get("query_discover", {})
        query_discover[self.user_id_field] = request.user.id
        query_discover[self._meta.datakey] = bundle.data.get(self._meta.datakey)

        return super(MongoUserResource, self).obj_create(
            bundle, request, query_discover=query_discover, **kwargs
        )
