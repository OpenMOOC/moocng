# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from moocng.externalapps.forms import ExternalAppForm
from moocng.externalapps.models import ExternalApp
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.models import Course


@is_teacher_or_staff
def externalapps_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    external_apps = ExternalApp.objects.filter(course=course)

    return render_to_response('externalapps_list.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'external_apps': external_apps,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def externalapps_add_or_edit(request, course_slug, external_app_id=None):
    if external_app_id is None:
        external_app = None
        course = get_object_or_404(Course, slug=course_slug)
    else:
        external_app = get_object_or_404(ExternalApp, pk=external_app_id)
        course = external_app.course

    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = ExternalAppForm(request.POST, instance=external_app)
        if form.is_valid():
            external_app = form.save(commit=False)
            external_app.course = course
            try:
                external_app.save()
            except IntegrityError:
                 messages.error(request, _('That ip address already has an application of the type supplied with the specified slug'))
            return HttpResponseRedirect(reverse("externalapps_list", args=[course_slug]))
    else:
        form = ExternalAppForm(
            instance=external_app,
            initial={'status': external_app.status if external_app else ExternalApp.NOT_CREATED}
        )

    return render_to_response('external_app_add_or_edit.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'form': form,
        'external_app': external_app,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def externalapps_delete(request, course_slug, external_app_id):
    external_app = get_object_or_404(ExternalApp, pk=external_app_id)
    external_app.delete()
    return HttpResponseRedirect(reverse("externalapps_list", args=[course_slug]))
