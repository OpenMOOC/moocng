from django.conf.urls import patterns, url


urlpatterns = patterns(
    'moocng.categories.views',
    url(r'^(?P<category_slug>[-\w]+)/$', 'category', name='category'),
)
