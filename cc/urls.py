from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from ccapp.views import ContactView, AboutView, MainView, FriendsView
from django.views.generic import TemplateView

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', MainView.as_view(), name='mainview'),
    url(r'^note/$',"ccapp.views.note"),
    url(r'^confirmIFS/(?P<pid>\d+)/(?P<secret>\d+)$','ccapp.views.confirmviewIFS'),
    url(r'^post/$','ccapp.views.createlistingviewIFS',name="createIFS"),
    url(r'^(?P<pid>\d+)$','ccapp.views.showpostIFS'),
    url(r'^delete/(?P<pid>\d+)$','ccapp.views.deletepostIFS'),
    url(r'^delete/all/','ccapp.views.deletepostIFS'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/$','ccapp.views.search'),
    url(r'^browse/$','ccapp.views.boxview',name="browse"),
    url(r'^ajax_box/$','ccapp.views.ajax_box'),
    url(r'^get_friend_notifications/$','ccapp.views.ajax_friend_notifications'),
    url(r'^about/$', AboutView.as_view()),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^message/(?P<pid>\d+)$', 'ccapp.views.contactsellerIFS'),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.SITE_ROOT + settings.STATIC_DOC_ROOT}),
    #dont put $ in front of these links or hell breaks lose
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^friends/$', FriendsView.as_view()),
    url(r'^fb_import/$', 'ccapp.views.fb_import', name='fb_import'),
    url(r'^groups/$', 'ccapp.views.all_circles', name="view_circles"),
    url(r'^groups/view/(?P<url_key>[\w\+%_& ]+)/$', 'ccapp.views.view_circle'),
    url(r'^groups/view/(?P<url_key>[\w\+%_& ]+)/delete/$', 'ccapp.views.delete_group'),
    url(r'^groups/view/(?P<url_key>[\w\+%_& ]+)/update/$', 'ccapp.views.update_group'),
    #url(r'^circles/view/(?P<url_key>[\w\+%_& ]+)/post/$', 'ccapp.views.createIFSwithinCircle'),
    url(r'^groups/create/$', 'ccapp.views.create_circle',name='createCircle'),
    url(r'^groups/search/$', 'ccapp.views.ajax_circle_search'), #XXX
    url(r'^canvas/', 'ccapp.views.canvas'),
    url(r'^user_posts/', 'ccapp.views.user_posts'),
    url(r'^bookmark/', 'ccapp.views.bookmark_post'),
    url(r'^verify_user/(?P<auth_key>[\w\+%_& ]+)/$','ccapp.views.verify_user'),
    url(r'^ajax_contact_seller/$','ccapp.views.ajax_contact_seller'),
    url(r'^ajax_delete_thread/$','ccapp.views.ajax_delete_thread'),
    url(r'^ajax_delete_post/$','ccapp.views.ajax_delete_post'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/successfully_logged_out/'}),

    
    url(r'', include('multiuploader.urls')),
    url(r'^privacy/', TemplateView.as_view(template_name = 'privacy_policy.html')),
    url(r'^feedback/', TemplateView.as_view(template_name = 'feedback.html')),
    url(r'^terms/', TemplateView.as_view(template_name= 'terms.html')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
