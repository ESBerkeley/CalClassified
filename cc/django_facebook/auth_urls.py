"""
URL patterns for the views included in ``django.contrib.auth``.

Including these URLs (via the ``include()`` directive) will set up the
following patterns based at whatever URL prefix they are included
under:

* User login at ``login/``.

* User logout at ``logout/``.

* The two-step password change at ``password/change/`` and
  ``password/change/done/``.

* The four-step password reset at ``password/reset/``,
  ``password/reset/confirm/``, ``password/reset/complete/`` and
  ``password/reset/done/``.

The default registration backend already has an ``include()`` for
these URLs, so under the default setup it is not necessary to manually
include these views. Other backends may or may not include them;
consult a specific backend's documentation for details.

"""

from django.conf.urls.defaults import *

from django.contrib.auth import views as auth_views
from cc.django_facebook import registration_views
from cc.django_facebook.utils import replication_safe
from cc.django_facebook import views as facebook

urlpatterns = patterns('',
                       url(r'^login/$',
                           replication_safe(auth_views.login),
                           {'template_name': 'registration/login.html'},
                           name='auth_login'),
                       url(r'^logout/$',
                           replication_safe(auth_views.logout),
                           {'template_name': 'registration/logout.html'},
                           name='auth_logout'),
                       url(r'^password/change/$',
                           auth_views.password_change,
                           name='auth_password_change'),
                       url(r'^password/change/done/$',
                           auth_views.password_change_done,
                           name='auth_password_change_done'),
                       url(r'^password/reset/$',
                           auth_views.password_reset,
                           name='auth_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           name='auth_password_reset_confirm'),
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           name='auth_password_reset_complete'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           name='auth_password_reset_done'),
                       url(r'^register/$',
                            registration_views.register,
                            name='registration_register'),
                       url(r'^login_calnet/$',
                            registration_views.login_calnet,
                            name='login_calnet'),
                       url(r'^profile/$',
                            'ccapp.views.profile_status',
                            name='account_profile'),
            #           url(r'^profile/posts/$',
            #                'ccapp.views.profile_posts',
            #                name='account_posts'),
                       url(r'^profile/settings/$',
                            'ccapp.views.profile_settings',
                            name='account_settings'),
                       url(r'^profile/messages/$',
                            'ccapp.views.profile_messages',
                            name='account_messages'),
                       url(r'^profile/selling/$',
                            'ccapp.views.profile_selling',
                            name='account_selling'),
                       url(r'^profile/buying/$',
                            'ccapp.views.profile_buying',
                            name='account_buying'),
                       url(r'^profile/messages/(?P<thread_id>\d+)$',
                            'ccapp.views.profile_view_thread',
                            name='account_thread'),
                       url(r'^profile/groups/$',
                            'ccapp.views.profile_circles',
                            name='account_circles'),
                       url(r'^profile/reviews/$',
                            'ccapp.views.profile_reviews',
                            name='account_reviews'),
                       url(r'^change_name/$', 'ccapp.views.change_name', name="auth_change_name")
)
