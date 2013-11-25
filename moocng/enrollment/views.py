from django.conf import settings
from django.contrib.messages import success
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from moocng.courses.models import Course
from moocng.enrollment.idp import enroll_course_at_idp


def free_enrollment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        user = request.user
        old_course_status = 'f'
        if course.created_from:
            if course.created_from.students.filter(pk=user.pk):
                old_course_status = 'n'
        course.students.through.objects.create(student=user,
                                               course=course,
                                               old_course_status=old_course_status)
        if getattr(settings, 'FREE_ENROLLMENT_CONSISTENT', False):
            enroll_course_at_idp(request.user, course)
        success(request,
                _(u'Congratulations, you have successfully enroll in the course %(course)s')
                % {'course': unicode(course)})

    return HttpResponseRedirect(reverse('course_overview',
                                        args=(course.slug, )))


def free_unenrollment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        user = request.user
        course.students.through.objects.get(student=user,
                                            course=course).delete()
        success(request,
                _(u'You have successfully unenroll in the course %(course)s')
                % {'course': unicode(course)})

    return HttpResponseRedirect(reverse('course_overview',
                                        args=(course.slug, )))
