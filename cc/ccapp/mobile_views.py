from ccapp.models import *
from ccapp.signals import post_created_signal
from ccapp.utils import *

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core import serializers
from django.db.models import Avg, Max, Min, Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse


from django_facebook.models import *
from django_facebook.api import get_facebook_graph, FacebookUserConverter
from open_facebook.exceptions import OpenFacebookException

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_view_exempt

from haystack.query import SearchQuerySet
from haystack.models import SearchResult

from math import ceil
from multiuploader.models import MultiuploaderImage

from django.core.mail import send_mail
from templated_email import send_templated_mail
import random
RANDOM_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('view_messages'))
    else:
        data = {}
        if "next" in request.GET:
            data['next'] = request.GET['next']
        return render_to_response('mobile/home.html', data, context_instance = RequestContext(request))

def browse(request):
    data = {}
    data['categories'] = Category.objects.all()
    data['max_price'] = int(ceil(ItemForSale.objects.aggregate(Max('price'))['price__max']))
    return render_to_response('mobile/browse.html',data,context_instance = RequestContext(request))

def login(request):
    return render_to_response('mobile/login.html',context_instance = RequestContext(request))

@login_required
def sell(request):
    user = request.user
    #user_profile = user.get_profile()

    if request.method == "GET":
        data = {}
        data['categories'] = Category.objects.all()
        return render_to_response('mobile/sell.html',data, context_instance = RequestContext(request))
    else:

        form = ItemForSaleForm(request.POST, request.FILES)#, instance=model_instance)
        #circles is generically added in front end
        if form.is_valid():
            model = form.save(commit=False)
            #model.is_confirmed = True
            #model.pk = request.POST[u'post_pk']
            model.owner = user
            model.save()

            files_list = request.FILES.getlist("images")
            for file in files_list:
                obj = MultiuploaderImage()
                obj.image = file
                obj.filename=str(file)
                obj.key_data = obj.key_generate
                obj.post = model
                obj.save()

            #circles weren't being saved cause commit=False, and a pk was need to add
            #manytomany relations
            circleQuery = Circle.objects.filter(name="Berkeley")
            model.circles = circleQuery
            model.save()

            post_created_signal.send(sender = ItemForSale, instance = model)

            return redirect(model.get_absolute_url())
        else:
            data={}
            data['categories'] = Category.objects.all()
            data['error'] = True
            data['form'] = form
            return render_to_response('mobile/sell.html',data,context_instance=RequestContext(request))


# AJAX VIEWS
def ajax_browse(request):

    #checked_circles = request.GET.getlist('circle')
    if "checked_categories[]" in request.GET:
        checked_categories = request.GET.getlist('checked_categories[]')
    else:
        checked_categories = []
        for category in Category.objects.all():
            checked_categories.append(category.id)

    min_price = 0
    max_price = float(ItemForSale.objects.aggregate(Max('price'))['price__max'])
    if ('max_price' in request.GET) and request.GET['max_price'].strip() and float(request.GET['max_price'])>= 0:
        max_price = float(request.GET['max_price'])
    if ('min_price' in request.GET) and request.GET['min_price'].strip() and float(request.GET['min_price'])>= 0:
        min_price = float(request.GET['min_price'])

    #if ('fbf' in request.GET) and request.GET['fbf'].strip() and float(request.GET['fbf'])>= 0:
    #    fbf=1

    #checked_circles = map(int,checked_circles))

    if ('searchText' in request.GET) and request.GET['searchText'].strip():
        query_string = request.GET['searchText']
        found_entries = SearchQuerySet().filter_or(text=query_string,category__in=checked_categories,price__range=(min_price,max_price)).order_by('-time_created')
    else:
        found_entries = SearchQuerySet().filter(category__in=checked_categories,price__range=(min_price,max_price)).order_by('-time_created')

    list_entries = []
    for entry in found_entries:
        list_entries.append(entry.object)

    data = serializers.serialize('json', list_entries)
    return HttpResponse(data,'application/javascript')

@login_required
def my_items(request):
    user = request.user
    items = ItemForSale.objects.filter(owner=user).order_by('-time_created')
    user_profile = user.get_profile()
    bookmarks = user_profile.bookmarks.all().order_by('-time_created')
    return render_to_response('mobile/my_items.html',
        {'items':items, 'bookmarks':bookmarks},
        context_instance=RequestContext(request))

def view_item(request,pid):
    if request.method == "GET":
        item = ItemForSale.objects.get(id = pid)
        image_set = item.get_image_set_urls()
        data = {}
        data['item'] = item
        data['image_set'] = image_set
        return render_to_response("mobile/view_item.html",data,context_instance = RequestContext(request))
    else:
        if request.is_ajax() and request.user.is_authenticated() and "message" in request.POST:
            send_bnm_message(request) # in utils.py

            return HttpResponse()

def ajax_message_send(request):
    if request.is_ajax() and request.user.is_authenticated() and request.method=="POST" and "message" in request.POST:
        send_bnm_message(request) # in utils.py

        return HttpResponse()

def message_sent(request):
    data = {}
    return render_to_response("mobile/message_sent.html",data,context_instance = RequestContext(request))


#ACCOUNT STUFF
@login_required
def view_messages(request):
    data = {}
    user = request.user
    my_threads = Thread.objects.filter(owner=user).order_by('is_read','-newest_message_time')
    for thread in my_threads:
        try:
            ItemForSale.objects.get(id=thread.post_id)
        except:
            thread.post_deleted = True
            thread.save()
    data['my_threads']= my_threads

    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    return render_to_response('mobile/view_messages.html',data,context_instance=RequestContext(request))

@login_required
def view_thread(request,thread_id):
    thread = Thread.objects.get(id = thread_id)

    try:
        item = ItemForSale.objects.get(id=thread.post_id)
    except:
        thread.post_deleted = True

    messages = thread.messages.all().order_by('-time_created')
    data = {"thread":thread, "messages": messages, "item": item}
    thread.is_read = True
    thread.save()
    return render_to_response('mobile/view_thread.html',data,context_instance=RequestContext(request))
