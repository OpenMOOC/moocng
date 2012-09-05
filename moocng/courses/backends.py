# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.contrib.auth.models import Group
from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ObjectDoesNotExist
from djangosaml2.backends import Saml2Backend


class Saml2BackendExtension(Saml2Backend):

    def update_user(self, user, attributes, attribute_mapping,
                force_save=False):
        """Update a user with a set of attributes and returns the updated user.

        By default it uses a mapping defined in the settings constant
        SAML_ATTRIBUTE_MAPPING. For each attribute, if the user object has
        that field defined it will be set, otherwise it will try to set
        it in the profile object.
        """
        if not attribute_mapping:
            return user

        try:
            profile = user.get_profile()
        except ObjectDoesNotExist:
            profile = None
        except SiteProfileNotAvailable:
            profile = None

        user_modified = False
        profile_modified = False
        for saml_attr, django_attrs in attribute_mapping.items():
            try:
                for attr in django_attrs:
                    if hasattr(user, attr):
                        if attr == 'groups':
                            group_ids = []
                            for value in attributes[saml_attr]:
                                try:
                                    id = Group.objects.get(name=value).id
                                    group_ids.append(id)
                                except DoesNotExist:
                                    pass
                            user.groups = group_ids
                        else:
                            setattr(user, attr, attributes[saml_attr][0])
                        user_modified = True
                    elif profile is not None and hasattr(profile, attr):
                        setattr(profile, attr, attributes[saml_attr][0])
                        profile_modified = True

            except KeyError:
                # the saml attribute is missing
                pass
        if user_modified or force_save:
            user.save()

        if profile is not None and (profile_modified or force_save):
            profile.save()

        return user
