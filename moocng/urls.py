from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from moocng.api.resources import UnitResource, KnowledgeQuantumResource


v1_api = Api(api_name='v1')
v1_api.register(UnitResource())
v1_api.register(KnowledgeQuantumResource())

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
