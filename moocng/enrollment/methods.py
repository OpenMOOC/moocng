from django import template
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from moocng.enrollment import BaseEnrollment


class FreeEnrollment(BaseEnrollment):

    name = 'free'
    title = _(u'Free enrollment')

    urls = patterns(
        'moocng.enrollment.views',
        url(r'^free-enroll/(?P<course_slug>[-\w]+)/$', 'free_enrollment', name='free_enrollment'),
        url(r'^free-unenroll/(?P<course_slug>[-\w]+)/$', 'free_unenrollment', name='free_unenrollment'),
        )

    def render_enrollment_button(self, context, course):
        tpl = template.loader.get_template('enrollment/free_enrollment_button.html')
        return tpl.render(context)

    def render_unenrollment_button(self, context, course):
        tpl = template.loader.get_template('enrollment/free_unenrollment_button.html')
        return tpl.render(context)
