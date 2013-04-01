from ccapp.models import *
from ccapp.signals import *
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
    return render_to_response('mobile/home.html', context_instance = RequestContext(request))

def login(request):
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
    if request.user.is_authenticated():
        return redirect(reverse('my_items'))
    else:
        data = {}
        if "next" in request.GET:
            data['next'] = request.GET['next']
        return render_to_response('mobile/login.html', data, context_instance = RequestContext(request))

def features(request):
    return render_to_response('mobile/features.html', context_instance = RequestContext(request))

def browse(request):
    data = {}
    data['categories'] = Category.objects.all()
    max_price = ItemForSale.objects.aggregate(Max('price'))['price__max']
    if max_price is None:
        max_price = 0
    else:
        max_price = ceil(float(max_price))
    data['max_price'] = max_price
    return render_to_response('mobile/browse.html',data,context_instance = RequestContext(request))

@login_required
def sell(request):
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
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
            model.get_thumbnail_url() #generate thumbnail

            post_created_signal.send(sender = ItemForSale, instance = model)

            return redirect(model.get_absolute_url())
        else:
            data={}
            data['categories'] = Category.objects.order_by('name')
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
    max_price = ItemForSale.objects.aggregate(Max('price'))['price__max']
    if max_price is None:
        max_price = 0
    else:
        max_price = float(max_price)
        
    if ('max_price' in request.GET) and request.GET['max_price'].strip() and float(request.GET['max_price'])>= 0:
        max_price = float(request.GET['max_price'])
    if ('min_price' in request.GET) and request.GET['min_price'].strip() and float(request.GET['min_price'])>= 0:
        min_price = float(request.GET['min_price'])

    #if ('fbf' in request.GET) and request.GET['fbf'].strip() and float(request.GET['fbf'])>= 0:
    #    fbf=1

    #checked_circles = map(int,checked_circles))

    try:
        page_num = int(request.GET['pageNum'])
    except:
        page_num = 1

    first_index = (page_num-1)*25
    last_index = page_num * 25

    if ('searchText' in request.GET) and request.GET['searchText'].strip():
        query_string = request.GET['searchText']
        found_entries = SearchQuerySet().filter_or(
            text=query_string,
            category__in=checked_categories,
            approved=True,
            sold=False,
            pending_flag=False,
            deleted=False,
            price__range=(min_price,max_price)).order_by('-time_created')[first_index:last_index]
    else:
        found_entries = SearchQuerySet().filter_or(
            category__in=checked_categories,
            approved=True,
            sold=False,
            pending_flag=False,
            deleted=False,
            price__range=(min_price,max_price)).order_by('-time_created')[first_index:last_index]

    list_entries = []
    for entry in found_entries:
        list_entries.append(entry.object)

    data = serializers.serialize('json', list_entries)
    return HttpResponse(data,'application/javascript')

@login_required
def my_items(request):
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
    #bookmarks = user_profile.bookmarks.all().order_by('-time_created')
    
    data = {}
    user = request.user

    selling_ids = [x.id for x in ItemForSale.objects.filter(owner=request.user).filter(sold = False).filter(deleted=False)]

    #sold_ids    = [x.id for x in ItemForSale.objects.filter(owner=request.user).filter(sold = True).filter(deleted=False)] #unused?? -seung

    ifs_waiting_list = ItemForSale.objects.filter(owner=request.user, pending_flag=False, deleted=False).order_by('-time_created')
    ifs_sold  = ItemForSale.objects.filter(owner=request.user, sold=True, deleted=False).order_by('-time_created')

    unsold_ids = [x.id for x in ifs_waiting_list]

    my_threads = Thread.objects.filter(owner=user,post_id__in=selling_ids).exclude(post_id__in=unsold_ids).order_by('is_read','-newest_message_time')  
    
    for thread in my_threads:
        try:
            ifs = ItemForSale.objects.get(id=thread.post_id)
            thread.post = ifs
        except:
            thread.post_deleted = True
            thread.save()

    data['my_threads'] = my_threads                #pending (need to exclude unsold threads)
    data['ifs_waiting_list'] = ifs_waiting_list    #unsold
    data['ifs_sold'] = ifs_sold                    #sold
    
    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    
    return render_to_response('mobile/my_items.html',
        data,
        context_instance=RequestContext(request))
        
@login_required
def buying(request):
    data = {}
    user = request.user

    pending_buying_ids = [x.id for x in ItemForSale.objects.filter(pending_buyer=request.user,pending_flag=True,sold=False)]
    completed_ids = [x.id for x in ItemForSale.objects.filter(pending_buyer=request.user).filter(sold=True)]

    my_threads = Thread.objects.filter(owner=user).filter(post_id__in=pending_buying_ids).order_by('is_read','-newest_message_time','-timestamp')

    completed_threads = Thread.objects.filter(owner=user).filter(post_id__in=completed_ids).order_by('is_read','-newest_message_time','-timestamp')

    for thread in my_threads:
        try:
            ifs = ItemForSale.objects.get(id=thread.post_id)
            thread.post = ifs
        except:
            thread.post_deleted = True
            thread.save()

    for thread in completed_threads:
        try:
            ItemForSale.objects.get(id=thread.post_id)
        except:
            thread.post_deleted = True
            thread.save()

    data['my_threads'] = my_threads
    data['completed_threads'] = completed_threads
    
    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    return render_to_response('mobile/buying.html',data,context_instance=RequestContext(request))

def view_item(request,pid):
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
    if request.method == "GET":
        item = ItemForSale.objects.get(id = pid)
        if item.deleted:
            data = {}
            data['message'] = "The item you are looking for has been deleted."
            return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
        
        image_set = item.get_image_set_urls()
        data = {}
        data['item'] = item
        data['image_set'] = image_set
        
        if item.pending_flag and item.pending_buyer == request.user:
            thread = Thread.objects.filter(owner=request.user, other_person=item.owner, post_id=item.id)
            if thread:
                data['thread'] = thread[0]
        elif item.pending_flag and item.owner == request.user:
            thread = Thread.objects.filter(owner=item.owner, post_id=item.id)
            if thread:
                data['thread'] = thread[0]
                
        relevant_comments = Comment.objects.filter(item = item).order_by('time_created')
        data['comments'] = relevant_comments
        
        return render_to_response("mobile/view_item.html",data,context_instance = RequestContext(request))
    
@login_required
def flag_item(request,pid):
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
    item = ItemForSale.objects.get(id=pid)
    flag, created = ItemFlag.objects.get_or_create(flagger = request.user, item=item)
    data = {}
    if created == False:
        data['title'] = "Item Flag Failed"
        data['message'] = "It looks like you already flagged this item. Email contact@buynear.me for further assistance."
        return render_to_response('mobile/message.html',data,context_instance=RequestContext(request)) 
    
    #check if more than 3 flags exist, if so get rid of the item and ban user
    flagged = ItemFlag.objects.filter(item = item)
    if len(flagged) >= 3 or request.user.is_staff:
        item.deleted = True
        item.save()
        owner = item.owner
        op = owner.get_profile()
        op.is_banned = True
        op.save()
        
        bad_items = ItemForSale.objects.filter(owner=owner)
        for bad in bad_items:
            bad.deleted = True
            bad.save()
        
        data['title'] = "Item Flagged"
        data['message'] = "Thanks for reporting this item. The item and user have been taken down!"
        return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
    data['title'] = "Item Flagged"
    data['message'] = "Thanks for reporting this item. If enough users report this item, it will be taken down. Please email contact@buynear.me for immediate moderation."
    return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))

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
    if request.user.is_authenticated() and request.user.get_profile().is_banned: #cy@hacker
        return HttpResponse("cy@m8")
    thread = Thread.objects.get(id = thread_id)
    if thread.owner != request.user:
        return redirect('/')

    try:
        item = ItemForSale.objects.get(id=thread.post_id)
    except:
        thread.post_deleted = True

    messages = thread.messages.all().order_by('-time_created')
    data = {"thread":thread, "messages": messages, "item": item}
    thread.is_read = True
    thread.save()
    return render_to_response('mobile/view_thread.html',data,context_instance=RequestContext(request))
    
@login_required
def notifications(request):
    """
    TYPES:
    1 - notify the seller that someone commented
    2- notify the commenter that the seller replied
    3 - notify the seller that someone clicked buy
    4 - notify the buyer that the seller has marked the sale complete
    5 - notify the buyer that the seller has given up on them, and reposted the item
    6 - notify the seller that the buyer has sent him a message
    7 - notify the buyer that the seller has sent him a message
    """
    user_profile = request.user.get_profile()
    user_profile.friend_notifications = 0
    user_profile.save()
    notifications = Notification.objects.filter(going_to = user_profile).order_by('-time_created')
    data = {}
    data['notifications'] = notifications
    return render_to_response('mobile/notifications.html',data,context_instance=RequestContext(request))
    
@login_required
def delete_item(request,pid):
    item = ItemForSale.objects.get(id=pid)
    if item.owner == request.user:
        item.deleted = True
        item.save()
        data = {}
        data['message'] = 'Your item has been deleted.'
        Notification.objects.filter(post_from=item).delete()
        return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
    else: #no permission
        data = {}
        data['message'] = "You don't have permission to do that, tsk tsk! >:("
        return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
        
@login_required
def item_action(request):
    #get request parameters required are
    # action - sold/fail  (self explanatory)
    # id - int of item id
    if "action" in request.GET and "id" in request.GET:
        data = {}
        action = request.GET['action']
        pid = request.GET['id']
        item = ItemForSale.objects.get(id=pid)
        if item.owner == request.user:        
            if action == "sold":
                item.sold = True
                item.save()
                data['title'] = "Transaction Complete"
                data['message'] = "Success! You have successfully marked your transaction as sold."
                sale_complete_signal.send(sender = ItemForSale, instance = item)
            elif action == "fail":
                repost_signal.send(sender = ItemForSale, instance = item, target = item.pending_buyer.get_profile())
                item.pending_flag = False
                item.save()
                data['title'] = "Transaction Failed"
                data['message'] = "You have marked the transaction to have failed and the item has been reposted."
                
            return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
                
        else:
            data = {}
            data['message'] = "You don't have permission to do that, tsk tsk! >:("
            return render_to_response('mobile/message.html',data,context_instance=RequestContext(request))
            
            
@login_required
def ajax_reply_comment(request):
    if request.method == "POST":
        commentID = request.POST['commentID']
        replyText = request.POST['replyText']
        comment = Comment.objects.get(id = commentID)
        if comment.item.owner == request.user:
            comment.seller_response = replyText
            comment.save()
            seller_response_signal.send(sender = Comment, instance = comment)
            return HttpResponse()

def ajax_send_comment(request):
    if request.method == "POST" and request.is_ajax():
        
        
        post_pk = request.POST['post_pk']
        item = ItemForSale.objects.get(id = int(post_pk))
       
        commentText = request.POST['commentText']
        comment = Comment.objects.create(sender=request.user, body=commentText, item=item)
        new_comment_signal.send(sender = Comment, instance = comment)
        return HttpResponse()
        
def ajax_delete_notifications(request):
    if request.method == "POST" and request.is_ajax():
        notifications = Notification.objects.filter(going_to = request.user.get_profile())
        notifications.delete()

        user_profile = request.user.get_profile()
        user_profile.friend_notifications = 0
        user_profile.save()
        return HttpResponse()
        
def banned(request):
    return HttpResponse("It seems you're banned. If you want to appeal email contact@buynear.me")
        
