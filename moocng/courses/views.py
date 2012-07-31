from django.contrib.messages import success
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import (get_object_or_404, get_list_or_404,
                              render_to_response)
from django.template import RequestContext
from django.utils.translation import ugettext as _

from moocng.courses.models import Course, Unit


def home(request):
    return render_to_response('courses/home.html', {
            'courses': Course.objects.all(),
            }, context_instance=RequestContext(request))


def course_overview(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.user.is_authenticated():
        is_enrolled = course.students.filter(id=request.user.id).exists()
    else:
        is_enrolled = False

    if request.method == 'POST':
        course.students.add(request.user)
        course.save()
        success(request,
                _(u'Congratulations, you have successfully enroll in the course %(course)s')
                % {'course': unicode(course)})
        return HttpResponseRedirect(reverse('course_overview',
                                            args=(course.slug, )))

    return render_to_response('courses/overview.html', {
            'course': course,
            'is_enrolled': is_enrolled
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
