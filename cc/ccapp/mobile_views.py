from ccapp.models import *
from ccapp.signals import post_created_signal

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core import serializers
from django.db.models import Avg, Max, Min, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import TemplateView

from django_facebook.models import *
from django_facebook.api import get_facebook_graph, FacebookUserConverter
from open_facebook.exceptions import OpenFacebookException

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_view_exempt

from haystack.query import SearchQuerySet
from haystack.models import SearchResult


from multiuploader.models import MultiuploaderImage

from django.core.mail import send_mail
from templated_email import send_templated_mail
import random
RANDOM_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def home(request):
    return render_to_response('mobile/home.html',context_instance = RequestContext(request))

def browse(request):
    return render_to_response('mobile/browse.html',context_instance = RequestContext(request))




# AJAX VIEWS
def ajax_browse(request):

    #checked_circles = request.GET.getlist('circle')
    #checked_categories = request.GET.getlist('category')
    """
    min_price = 0
    max_price = float(ItemForSale.objects.aggregate(Max('price'))['price__max'])
    if ('max_price' in request.GET) and request.GET['max_price'].strip() and float(request.GET['max_price'])>= 0:
        max_price = float(request.GET['max_price'])
    if ('min_price' in request.GET) and request.GET['min_price'].strip() and float(request.GET['min_price'])>= 0:
        min_price = float(request.GET['min_price'])

    if ('fbf' in request.GET) and request.GET['fbf'].strip() and float(request.GET['fbf'])>= 0:
        fbf=1

    checked_circles = map(int,checked_circles)
    checked_categories = map(int, checked_categories)
    """

    """ #OLD NON-HAYSTACK SEARCH
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'body','category__name','circles__name'])
        found_entries = found_entries.filter(entry_query).order_by('-time_created')
    """

    if ('searchText' in request.GET) and request.GET['searchText'].strip():
        query_string = request.GET['searchText']
        found_entries = SearchQuerySet().filter_or(text=query_string)#,circles__in=checked_circles,category__in=checked_categories,price__range=(min_price,max_price)).order_by('-time_created')
        #found_entries = SearchQuerySet().filter(text=query_string)
        #found_entries = found_entries.filter(entry_query) #auto orders by relevance score
    else:
        found_entries = SearchQuerySet().filter()#circles__in=checked_circles,category__in=checked_categories,price__range=(min_price,max_price)).order_by('-time_created')

    list_entries = []
    for entry in found_entries:
        list_entries.append(entry.object)

    data = serializers.serialize('json', list_entries)
    return HttpResponse(data,'application/javascript')