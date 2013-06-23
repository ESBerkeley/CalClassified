__author__ = 'seung' #lol pycharm did this

from django.conf import settings
import re
from django.contrib.auth import logout

class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        #request.subdomain = ''
        parts = request.domain.split('.')

        if parts[0] == "m":
            is_mobile = True
        else:
            is_mobile = False

        # set the right urlconf
        if is_mobile:
            request.urlconf = 'cc.mobile_urls'
        else:
            request.urlconf = 'cc.urls'

class ActiveUserMiddleware:
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        user_profile = request.user.get_profile()
        if user_profile.is_banned:
            logout(request)
        if user_profile.facebook_id and not user_profile.is_connected(request):
            logout(request)