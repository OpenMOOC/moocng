from django.contrib.messages import success
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from moocng.courses.models import Course


def free_enrollment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        course.students.add(request.user)
        course.save()
        success(request,
                _(u'Congratulations, you have successfully enroll in the course %(course)s')
                % {'course': unicode(course)})

    return HttpResponseRedirect(reverse('course_overview',
                                        args=(course.slug, )))


def free_unenrollment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        course.students.remove(request.user)
        course.save()
        success(request,
                _(u'You have successfully unenroll in the course %(course)s')
                % {'course': unicode(course)})

    return HttpResponseRedirect(reverse('course_overview',
                                        args=(course.slug, )))
