from django.conf.urls import include, patterns, url
from django.conf import settings


urlpatterns = patterns(
    '',
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    (r'', include('registration.backends.default.urls')),
)
