from django.conf.urls import patterns, url


urlpatterns = patterns(
    'moocng.categories.views',
    url(r'^(?P<categories>[-\w/]+)/$', 'category', name='category'),
)
