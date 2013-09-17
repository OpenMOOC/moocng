# -*- coding: utf-8 -*-
from django import template

from moocng.courses.models import Course
from moocng.externalapps.models import ExternalApp

register = template.Library()


@register.inclusion_tag('courses/external_apps.html', takes_context=True)
def externalapps(context):
    course = context['course']
    course_slug = course.slug
    course = Course.objects.filter(slug=course_slug)
    external_apps = ExternalApp.objects.filter(course=course)
    return {'external_apps': external_apps}
