from django.conf.urls import patterns, url

from .views import Category


urlpatterns = patterns(
    'moocng.categories.views',
    url(r'^(?P<categories>[-\w/]+)/$', Category.as_view(), name='category'),
)
