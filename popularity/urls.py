from django.conf.urls.defaults import *

urlpatterns = patterns('popularity.views',
    url(r'^$', 'Popular', name='popular'),
    url(r'^page/(?P<page>\d+)/?$', 'Popular'),
)
