from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def askboturl(course_slug):
    try:
        return settings.ASKBOT_URL_TEMPLATE % course_slug
    except AttributeError:
        return '#'

