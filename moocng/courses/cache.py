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

from django.conf import settings
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote


def get_template_fragment_key(fragment, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    return 'template.cache.%s.%s' % (fragment, args.hexdigest())


def invalidate_template_fragment(fragment, *variables):
    cache_key = get_template_fragment_key(fragment, *variables)
    if cache_key in cache:
        cache.delete(cache_key)


def invalidate_template_fragment_i18n(fragment, *variables):
    for lang_code, lang_text in settings.LANGUAGES:
        i18n_variables = (lang_code,) + variables
        invalidate_template_fragment(fragment, *i18n_variables)
