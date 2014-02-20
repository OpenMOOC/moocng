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

from django.template import Library, TemplateSyntaxError, resolve_variable
from django.templatetags.cache import CacheNode

register = Library()


class ConditionalCacheNode(CacheNode):

    def __init__(self, nodelist, condition, expire_time_var, fragment_name, vary_on):
        self.condition = condition
        super(ConditionalCacheNode, self).__init__(nodelist, expire_time_var, fragment_name, vary_on)

    def render(self, context):
        use_cache = resolve_variable(self.condition, context)
        if not use_cache:
            return self.nodelist.render(context)
        return super(ConditionalCacheNode, self).render(context)


@register.tag('conditionalcache')
def do_conditional_cache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load conditionalcache %}
        {% conditionalcache [use_cache] [expire_time] [fragment_name] %}
            .. some expensive processing ..
        {% endconditionalcache %}

    This tag also supports varying by a list of arguments::

        {% load conditionalcache %}
        {% conditionalcache [use_cache] [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endconditionalcache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endconditionalcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise TemplateSyntaxError(u"'%r' tag requires at least 3 arguments." %
                                  tokens[0])
    return ConditionalCacheNode(nodelist, tokens[1], tokens[2], tokens[3],
                                tokens[4:])
