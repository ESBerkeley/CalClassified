from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from ccapp.views import ContactView, AboutView, MainView, FriendsView
from django.views.generic import TemplateView

admin.autodiscover()


urlpatterns = patterns('',
    #MAIN PAGES
    url(r'^$', MainView.as_view(), name='mainview'),
    url(r'^browse/$','ccapp.views.boxview',name="browse"),
    url(r'^sell/$','ccapp.views.createlistingviewIFS',name="createIFS"),
    url(r'^post/$','ccapp.views.createlistingviewIFS',name="createIFS"), #delete in future, in case for hard links
    url(r'^about/$', AboutView.as_view()),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^privacy/', TemplateView.as_view(template_name = 'privacy_policy.html')),
    url(r'^feedback/', TemplateView.as_view(template_name = 'feedback.html')),
    url(r'^terms/', TemplateView.as_view(template_name= 'terms.html')),
    url(r'^(?P<pid>\d+)$','ccapp.views.showpostIFS'),

    #ACCOUNT:
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^fb_import/$', 'ccapp.views.fb_import', name='fb_import'),
    url(r'^account_setup/$', 'ccapp.views.account_setup', name='account_setup'),

    #ADMIN/DEBUG
    url(r'^friends/debug/$', 'ccapp.views.friendslist', name='test_friends'),
    url(r'^fb_items/$', 'ccapp.views.fb_items', name='add_fb_items'),
    url(r'^fb_admin/$', 'ccapp.views.fb_admin', name='approve_fb_items'),

    #??? not sure if functional still
    url(r'^confirmIFS/(?P<pid>\d+)/(?P<secret>\d+)$','ccapp.views.confirmviewIFS'),

    #BACK-END -------
    url(r'^note/$',"ccapp.views.note"),

    url(r'^delete/(?P<pid>\d+)$','ccapp.views.deletepostIFS'),
    url(r'^delete/all/','ccapp.views.deletepostIFS'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/$','ccapp.views.search'),

    url(r'^ajax_box/$','ccapp.views.ajax_box'),
    url(r'^get_friend_notifications/$','ccapp.views.ajax_friend_notifications'),

    url(r'^clear_notifications/$','ccapp.views.delete_notifications'),
    url(r'^about/$', AboutView.as_view()),
    url(r'^contact/$', ContactView.as_view()),

    url(r'^message/(?P<pid>\d+)$', 'ccapp.views.contactsellerIFS'),
    url(r'^modify_post/','ccapp.views.modify_post'),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.SITE_ROOT + settings.STATIC_DOC_ROOT}),
#    url(r'^buynow/$','ccapp.views.buynow'),
    #dont put $ in front of these links or hell breaks lose

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
                          {'next_page': '/'}),

    url(r'', include('multiuploader.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
