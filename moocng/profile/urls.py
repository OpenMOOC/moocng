from django.conf.urls import include, patterns, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse


urlpatterns = patterns(
    'moocng.profile.views',
    url(r'^user/timeline$', 'profile_timeline',
        name='profile_timeline'),
    url(r'^user/groups$', 'profile_groups',
        name='profile_groups'),
    url(r'^user/courses$', 'profile_courses',
        name='profile_courses'),
    url(r'^user/calendar$', 'profile_calendar',
        name='profile_calendar'),
    url(r'^user/profile$', 'profile_user',
        name='profile_user'),
)
