from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('imageupload.views',
    url(r'^upload/$','upload_image', name='img'),
)

urlpatterns += staticfiles_urlpatterns()
