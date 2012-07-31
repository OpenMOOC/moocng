from django.shortcuts import (get_object_or_404, get_list_or_404,
                              render_to_response)
from django.template import RequestContext

from moocng.courses.models import Course, Unit


def home(request):
    return render_to_response('courses/home.html', {
            'courses': Course.objects.all(),
            }, context_instance=RequestContext(request))


def course_overview(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    return render_to_response('courses/overview.html', {
            'course': course,
            }, context_instance=RequestContext(request))


def course_classroom(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    unit_list = get_list_or_404(Unit, course=course)

    return render_to_response('courses/classroom.html', {
        'course': course,
        'unit_list': unit_list,
    }, context_instance=RequestContext(request))


def course_progress(request):
    pass
