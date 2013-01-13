from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()


urlpatterns = patterns('ccapp.mobile_views',
    url(r'^$', "home", name='home'),
    url(r'^browse/$',"browse", name="browse"),
    url(r'^sell/$',"sell", name="sell"),
    url(r'^features',"features", name="features"),
    url(r'^my_items/$',"my_items", name="my_items"),
    url(r'^login',"login", name="login"),
    url(r'^(?P<pid>\d+)$','view_item'),
    url(r'^dialog/message_sent/$','message_sent', name="message_sent"),

    url(r'^accounts/login/$',auth_views.login,{'template_name': 'mobile/home.html'},name='auth_login'),

    #FACEBOOK
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),

    #AJAX URLS
    url(r'^ajax/browse/$',"ajax_browse", name="ajax_browse"),
    url(r'^ajax/send_message/$',"ajax_message_send", name="ajax_message_send"),

    #ACCOUNT URLS
    url(r'^view_messages/$',"view_messages", name="view_messages"),
    url(r'^view_messages/(?P<thread_id>\d+)/$',"view_thread"),

                        ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
)
