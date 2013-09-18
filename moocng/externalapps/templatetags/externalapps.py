# -*- coding: utf-8 -*-
from django import template

from moocng.courses.models import Course
from moocng.externalapps.models import ExternalApp

register = template.Library()


@register.simple_tag
def get_icon_for_status(external_app):
    icons = {
        ExternalApp.CREATED: 'icon-ok',
        ExternalApp.NOT_CREATED: 'icon-warning-sign',
        ExternalApp.IN_PROGRESS: 'icon-time',
        ExternalApp.ERROR: 'icon-warning-sign',
    }
    if external_app:
        icon = icons.get(external_app.status, '')
    else:
        icon = ''
    return icon


@register.inclusion_tag('courses/external_apps.html', takes_context=True)
def externalapps_list(context):
    course = context['course']
    course_slug = course.slug
    course = Course.objects.filter(slug=course_slug)
    external_apps = ExternalApp.objects.filter(course=course)
    return {'external_apps': external_apps}
