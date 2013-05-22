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


from django import template

from moocng.mongodb import get_db
from moocng.assets.utils import course_has_assets
from moocng.assets.models import Asset

register = template.Library()


class IfHasAssetsNode(template.Node):

    def __init__(self, course, nodelist_true, nodelist_false):
        self.course = template.Variable(course)
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfHasAssetsNode>"

    def render(self, context):
        course = self.course.resolve(context)
        if course_has_assets(course):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag
def if_has_assets(parser, token):
    bits = token.contents.split()

    try:
        course = bits[1]
    except IndexError:
        raise template.TemplateSyntaxError('%r tag requires a single argument'
                                           % bits[0])

    nodelist_true = parser.parse(('else', 'endif_has_assets'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_has_assets', ))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return IfHasAssetsNode(course, nodelist_true, nodelist_false)
