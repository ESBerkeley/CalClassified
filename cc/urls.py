from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from ccapp.views import ContactView, AboutView,  FeedbackView, ThanksView #,MainView
from django.views.generic import TemplateView

admin.autodiscover()


urlpatterns = patterns('',
    #MAIN PAGES
    #url(r'^$', MainView.as_view(), name='mainview'),
    url(r'^$','ccapp.views.index_home',name="mainview"),
    url(r'^browse/$','ccapp.views.boxview',name="browse"),
    url(r'^sell/$', 'ccapp.views.sell_item_IFS', name="createIFS"),
    url(r'^post/$', 'ccapp.views.sell_item_IFS', name="sell_item"), #delete in future, in case for hard links
    url(r'^sell_item/$', 'ccapp.views.sell_item_POST', name="sell_item_POST"),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^team/$', TemplateView.as_view(template_name='team.html'), name="team"),
    url(r'^testimonials/$', TemplateView.as_view(template_name='testimonials.html'), name="testimonials"),
    url(r'^faq/$', TemplateView.as_view(template_name='faq.html'), name="faq"),
    url(r'^timeline/$', TemplateView.as_view(template_name='timeline.html'), name="timeline"),
    url(r'^how_it_works/$', TemplateView.as_view(template_name='how_it_works.html'), name="how_it_works"),
    url(r'^jobs/$', TemplateView.as_view(template_name='jobs.html'), name="jobs"),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^privacy/$', TemplateView.as_view(template_name='privacy_policy.html'), name="privacy"),
    url(r'^feedback/$', FeedbackView.as_view(), name="feedback"),
    url(r'^thanks/', ThanksView.as_view(), name='thanks'),
    url(r'^terms/$', TemplateView.as_view(template_name='terms.html'), name="terms"),
    url(r'^(?P<pid>\d+)$','ccapp.views.showpostIFS'),
    url(r'^repost/$', 'ccapp.views.repost_item', name='repost_item'),
    url(r'^ajax_repost/$', 'ccapp.views.ajax_repost_item', name='ajax_repost_item'),
    url(r'^pay_for_item/$', 'ccapp.views.pay_for_item', name='pay_for_item'),


    #ACCOUNT:
    url(r'^facebook/', include('django_facebook.urls')),
    #EVERY URL THAT STARTS WITH "/accounts/" IS IN django_facebook.auth_urls
    url(r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^fb_import/$', 'ccapp_facebook.views.fb_import', name='fb_import'),
    url(r'^account_setup/$', 'ccapp.views.account_setup', name='account_setup'),
    url(r'^verify_user/(?P<auth_key>[\w\+%_& ]+)/$','ccapp.views.verify_user'),
    url(r'^change_email/(?P<auth_key>[\w\+%_& ]+)/$','ccapp.views.change_email'),
    url(r'^user/(?P<user_id>\d+)/$', 'ccapp.views.user', name='user'),

    #ADMIN/DEBUG
    url(r'^friends/debug/$', 'ccapp_facebook.views.friendslist', name='test_friends'),
    #url(r'^fb_items/$', 'ccapp.views.fb_items', name='add_fb_items'),
    #url(r'^fb_admin/$', 'ccapp.views.fb_admin', name='approve_fb_items'),
    #url(r'^fb_to_excel/$', 'ccapp_faceboook.views.fb_to_excel', name='fb_to_excel'),

    #??? not sure if functional still
    #url(r'^confirmIFS/(?P<pid>\d+)/(?P<secret>\d+)$','ccapp.views.confirmviewIFS'),

    #BACK-END -------
    url(r'^note/$',"ccapp.views.note"),

    url(r'^delete/(?P<pid>\d+)$','ccapp.views.deletepostIFS'),
    url(r'^edit/(?P<pid>\d+)/$','ccapp.views.edit_item', name='edit_item'),
    url(r'^flag/(?P<pid>\d+)/$','ccapp.views.flag_item', name='flag_item'),
    url(r'^delete/all/','ccapp.views.deletepostIFS'),
    url(r'^admin_user/', include(admin.site.urls)),
    #url(r'^search/$','ccapp.views.search'), NOT USED???

    url(r'^ajax_box/$','ccapp.views.ajax_box'),
    url(r'^get_friend_notifications/$','ccapp.views.ajax_friend_notifications'),

    url(r'^clear_notifications/$','ccapp.views.delete_notifications'),
    url(r'^about/$', AboutView.as_view()),
    url(r'^contact/$', ContactView.as_view()),

    #url(r'^message/(?P<pid>\d+)$', 'ccapp.views.contactsellerIFS'),
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

    #AJAX
    url(r'^ajax_contact_seller/$','ccapp.views.ajax_contact_seller'),
    url(r'^ajax_delete_thread/$','ccapp.views.ajax_delete_thread'),
    url(r'^ajax_delete_post/$','ccapp.views.ajax_delete_post'),
    url(r'^ajax/delete_comment/(?P<comment_id>\d+)/$','ccapp.views.ajax_delete_comment', name='ajax_delete_comment'),
    url(r'^ajax/delete_response/(?P<comment_id>\d+)/$','ccapp.views.ajax_delete_response', name='ajax_delete_response'),
    url(r'^ajax/upload_temp_photo/$', 'ccapp.views.upload_temp_photo', name='ajax_upload_temp_photo'),
    url(r'^ajax/upload_profile_photo/$', 'ccapp.views.upload_profile_photo', name='ajax_upload_profile_photo'),
    url(r'^ajax/delete_profile_photo/$', 'ccapp.views.delete_profile_photo', name='ajax_delete_profile_photo'),

    url(r'^logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/'}),
    url(r'', include('multiuploader.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
