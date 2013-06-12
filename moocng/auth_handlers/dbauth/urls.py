from django.conf.urls import include, patterns, url
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse
from django.conf import settings

urlpatterns = patterns(
    '',
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    url(r'^login/$', redirect_to, { 'url': '/auth/djangoauth/login/' }, name='login'),
    url(r'^register/$', redirect_to, { 'url': '/auth/djangoauth/register/' }, name='register'),
    url(r'^profile/$', 'moocng.auth_handlers.dbauth.views.profile', name='profile'),
    url(r'^password/change/$', redirect_to, { 'url': '/auth/djangoauth/password/change/' }, name='changepw'),

    (r'^djangoauth/', include('registration.backends.default.urls')),
)
