# Copyright 2013 Rooter Analysis S.L.
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

from django.core.cache import cache


def get_course_key(course):
    return 'course_%d_has_assets' % course.id


def get_course_has_assets_from_cache(course):
    return cache.get(get_course_key(course))


def set_course_has_assets_in_cache(course, has_assets):
    cache.set(get_course_key(course), has_assets, 3600)


def invalidate_course_has_assets_in_cache(course):
    cache.delete(get_course_key(course))
