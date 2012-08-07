from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from moocng.api.resources import (UnitResource, KnowledgeQuantumResource,
                                  QuestionResource, OptionResource)


v1_api = Api(api_name='v1')
v1_api.register(UnitResource())
v1_api.register(KnowledgeQuantumResource())
v1_api.register(QuestionResource())
v1_api.register(OptionResource())

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'moocng.views.home', name='home'),
    url(r'^', include('moocng.courses.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^api/', include(v1_api.urls)),
)

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)
