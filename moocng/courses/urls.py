from django.conf.urls import patterns, url


urlpatterns = patterns(
    'moocng.courses.views',
    url(r'^$', 'home', name='home'),

    url(r'^course/(?P<course_slug>[-\w]+)$', 'course_overview',
        name='course_overview'),
    url(r'^course/(?P<course_slug>[-\w]+)/classroom$', 'course_classroom',
        name='course_classroom'),
    url(r'^course/(?P<course_slug>[-\w]+)/progress$', 'course_progress',
        name='course_progress'),
    )
