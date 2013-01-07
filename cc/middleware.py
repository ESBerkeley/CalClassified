__author__ = 'seung' #lol pycharm did this

from django.conf import settings
import re

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