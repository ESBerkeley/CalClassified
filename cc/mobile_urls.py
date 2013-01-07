from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('ccapp.mobile_views',
                       url(r'^$', "home", name='home'),
                       url(r'^browse/$',"browse", name="browse"),


                       #AJAX URLS
                       url(r'^ajax/browse/$',"ajax_browse", name="ajax_browse"),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
