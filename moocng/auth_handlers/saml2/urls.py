from django.conf.urls import include, patterns, url
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse
from django.conf import settings


urlpatterns = patterns(
    '',
    url(r'^logout/$', redirect_to, { 'url': '/auth/saml2/logout/' }, name='logout'),
    url(r'^login/$', redirect_to, { 'url': '/auth/saml2/login/' }, name='login'),
    url(r'^register/$', redirect_to, { 'url': settings.REGISTRY_URL }, name='register'),
    url(r'^profile/$', redirect_to, { 'url': settings.PROFILE_URL }, name='profile'),
    url(r'^password/change/$', redirect_to, { 'url': settings.CHANGEPW_URL }, name='changepw'),
    url('^saml2/', include('djangosaml2.urls'))
)
