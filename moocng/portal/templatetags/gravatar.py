# Copyright 2013 UNED
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

import urllib

from django import template
from django.conf import settings
from django.utils.hashcompat import md5_constructor
from django.utils.safestring import mark_safe


GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", None)


register = template.Library()


@register.simple_tag
def gravatar_for_email(email):
    url = "%savatar/%s?d=mm" % (GRAVATAR_URL_PREFIX, md5_constructor(email).hexdigest())
    if GRAVATAR_DEFAULT_IMAGE is not None:
        url += "?%s" % urllib.urlencode({"default": GRAVATAR_DEFAULT_IMAGE})
    return mark_safe(url)


@register.simple_tag
def gravatar_img_for_email(email, size=80):
    url = gravatar_for_email(email)
    img = '<img src="%s" height="%s" width="%s"/>' % (url, size, size)
    return mark_safe(img)
