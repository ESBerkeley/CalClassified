from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core import serializers
from django.db.models import Avg, Max, Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from haystack.query import SearchQuerySet
from django.core.mail import send_mail

from cc.swamp_logging import logit, custom_log_message
from cc.ccapp.models import *
from cc.ccapp.signals import *
from cc.ccapp.utils import *
from cc.ccapp.forms import EmailForm, FeedbackForm, CreditCardForm
from cc.django_facebook.decorators import facebook_required
from cc.multiuploader.models import MultiuploaderImage
from cc.templated_email import send_templated_mail

#for image rotate
from PIL import Image
#

import random
import datetime

RANDOM_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

@csrf_exempt
def canvas(request):
    data = {}
    data['request_ids'] = []
    if 'request_ids' in request.GET:
        request_ids = str(request.GET['request_ids'])
        request_ids = request_ids.split(',')
        data['request_ids'] = request_ids
    return render_to_response('canvas.html', data, context_instance = RequestContext(request))

def note(request):
    title = request.GET['title']
    msg = request.GET['msg']
    return render_to_response('message.html',{'title':title,'message':msg},context_instance=RequestContext(request))


def ajax_circle_search(request): 
    if request.is_ajax() or True:
        user_profile = request.user.get_profile()
        my_circles = user_profile.my_circles.all()
        my_circles_id = [o.id for o in my_circles]

        results = Circle.objects.filter(is_public=True).exclude(id__in=my_circles_id)
        
        #if 'query' in request.GET:
        #    results = results.filter(name__contains = request.GET['query'])

        if ('query' in request.GET) and request.GET['query'].strip():
            query_string = request.GET['query']
            entry_query = get_query(query_string, ['name'])
            results = results.filter(entry_query)#.order_by('-time_created')
            
        data = serializers.serialize('json', results, indent = 4, extras=('get_absolute_url',))
        return HttpResponse(data,'application/javascript')
    else:
        return HttpResponse("oi")
    
class FriendsView(TemplateView):
    template_name = 'friends.html'

#class MainView(TemplateView):
#    template_name = 'index.html'

def index_home(request):
    return render_to_response('index.html',context_instance=RequestContext(request))


class FeedbackView(FormView):
    template_name = 'feedback.html'
    form_class = FeedbackForm
    success_url = '/thanks/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        user = self.request.user
        try:
            full_name = user.get_full_name()
        except:
            full_name = 'No Name'
        send_templated_mail(
            template_name='feedback',
            from_email='noreply@buynear.me',
            recipient_list=['feedback@buynear.me'],
            context={
                'message':form.cleaned_data['message'],
                'username':user.username,
                'email':form.cleaned_data['email'],
                'full_name':full_name
                },
        )
        return super(FeedbackView, self).form_valid(form)


class ThanksView(TemplateView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        context = super(ThanksView, self).get_context_data(**kwargs)
        context['title'] = 'Thanks for the feedback!'
        context['message'] = 'We hope you had a great experience, and we hope to make it even better!'
        return context

"""def confirmview(request,pid,secret,super_cat):
    try:
        post = super_cat.objects.get(pk=pid)
        if post.is_confirmed == True:
            return render_to_response("message.html",{'message':'Already confirmed'},context_instance=RequestContext(request))
        elif post.secret_code == secret:
            post.is_confirmed = True
            post.save()
            return HttpResponse('Success!')
        else:
            return HttpResponse('Invalid Code')

    except super_cat.MultipleObjectsReturned:
        return HttpResponse('Duplicate Post Code')
    except super_cat.DoesNotExist:
        return HttpResponse('Post Does Not Exist')

def confirmviewIFS(request,pid,secret):
    confirmview(request,pid,secret,ItemForSale)"""

@logit
@facebook_required(scope='publish_actions')
def sell_item(request, super_cat_form, super_cat_model,**kwargs):
    if request.user.is_authenticated():
        
        user = request.user
        user_profile = user.get_profile()

        #MULTIUPLOADER COMMENTS
        #model = super_cat_model()
        #model.key_data = model.key_generate

        #form variable gets rewritten in 'if' statement if its within circle
        form = super_cat_form()#instance=model)
        #form.fields['circles'].queryset = user_profile.my_circles.all()
        #form.fields['circles'].label = "Groups"
        #form.fields['circles'].help_text = """Tip: Hold down "Control", or "Command" on a Mac, to select more than one.
        #    <p style="color:red;">Only people in the groups you select can see your post.</p>"""
        #Specify which groups you want to sell to.

        #Saving model for MULTIUPLOADER
        #request.session['instance'] = model
        #ecks = {'post_key':model.key_data}
        ecks = {}
        if len(user_profile.my_circles.all()) == 0:
            ecks['no_circles'] = True

        #CODE IF IFS CREATED WITHIN SECRET CIRCLE
        #if 'url_key' in kwargs:
        #    url_key = kwargs['url_key']
        #    circles = Circle.objects.filter(url_key=url_key)
        #    circle = circles[0]
        #    ecks['specificCircleName']=circle.name
        #    form = ItemForSaleForm(initial={'circles':circles},instance=model)

        ecks['form'] = form
        if user_profile.facebook_id:
            ecks['is_facebook'] = True
            #user_profile.extend_access_token()
            groups = FacebookGroup.objects.filter(user_id = user.id).order_by('bookmark_order')
            ecks['fb_groups'] = groups
        ecks.update(csrf(request))
        return render_to_response('sell_item.html',ecks,context_instance=RequestContext(request))


def sell_item_POST(request):
    if request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        if request.method == 'POST':
            #try:
             #   model_instance = request.session['instance']
            #except:
            #    model_instance = None
            form = ItemForSaleForm(request.POST, request.FILES)#, instance=model_instance)
            if form.is_valid():
                model = form.save(commit=False)
                #model.is_confirmed = True
                #model.pk = request.POST[u'post_pk']
                model.owner = user
                model.owner_facebook_id = user.get_profile().facebook_id
                #MULTIUPLOADER
                #images = MultiuploaderImage.objects.filter(post_key_data=model.key_data)

                model.save()

                files_list = request.FILES.getlist("images")
                for index, file in enumerate(files_list):
                    obj = MultiuploaderImage()
                    image = Image.open(file)
                    rotate_name = "rotate-value" + str(index)
                    print float(request.POST[rotate_name])
                    obj.image = image_rotate(image, float(request.POST[rotate_name]), str(file))
                    obj.filename = str(file)
                    obj.key_data = obj.key_generate
                    obj.post = model
                    obj.save()
                    #model.image_set.add(obj)

                #circles weren't being saved cause commit=False, and a pk was need to add
                #manytomany relations
                #circleIDs = request.POST.getlist('circles')
                #circleQuery = Circle.objects.filter(id__in=circleIDs)
                #model.circles = circleQuery
                model.circles = user_profile.my_circles.all()
                model.save()
                model.get_thumbnail_url() #generrate thumbnail

                #MULTIUPLOADER
                #for image in images:
                #    image.post = model
                #    image.save()
                fb_success = False
                fb_group_success = True
                group_ids = request.POST.getlist('fb_groups')
                links = []
                for group_id in group_ids:
                    # group = FacebookGroup.objects.get(facebook_id=group_id)
                    if group_id: #first elem always empty
                        success = fb_group_post(request, model, str(group_id)+'/feed')
                        if success:
                            try:
                                links.append(tuple(success['id'].split('_')))
                                fb_success = True
                            except:
                                fb_group_success = False
                        else:
                            fb_group_success = False
                post_created_signal.send(sender = ItemForSale, instance = model)
                if not fb_group_success:
                    return redirect(model.get_absolute_url()+"?new=1&postffs=0")
                elif not fb_success:
                    return redirect(model.get_absolute_url()+"?new=1")
                else:
                    request.session['links'] = links
                    return redirect(model.get_absolute_url()+"?new=1&postffs=2")

            else:
                return render_to_response('sell_item.html',{'form':form},context_instance=RequestContext(request))
        else:
            form = ItemForSaleForm()
            return render_to_response('sell_item.html',{'form':form},context_instance=RequestContext(request))
    else:
        redirect("/accounts/login/")


@login_required
def sell_item_IFS(request):
    return sell_item(request, ItemForSaleForm, ItemForSale)

def pay_for_item(request):
    form = CreditCardForm()
    return render_to_response('pay_for_item.html',{'form':form},context_instance=RequestContext(request))



#def createIFSwithinCircle(request, url_key):
#    return createlistingview(request,ItemForSaleForm,ItemForSale,url_key=url_key)


@login_required
@logit
def deletepost(request, pid, super_cat):
    if request.user.is_authenticated():
        user = request.user
        #user_profile = user.get_profile()
        try:
            post = super_cat.objects.get(pk=pid)
            if post.owner == user:
                post.delete()
                return render_to_response('message.html',{'title':'Post Deleted','message':'Your post has been deleted!'},context_instance=RequestContext(request))
            else:
                return render_to_response('message.html',{'title':'Deletion Failed','message':'You do not have permissions to delete this post.'},context_instance=RequestContext(request)) 
        except:
            return render_to_response('message.html',{'title':'Deletion Failed','message':'Oh No! Post does not exist!'},context_instance=RequestContext(request))

def deletepostIFS(request, pid):
    return deletepost(request,pid,ItemForSale)

@login_required
@logit
def ajax_delete_post(request):
    if request.method == "POST" and request.is_ajax():
        post_id = request.POST['post_id']
        post = ItemForSale.objects.get(pk=post_id)
        if post.owner == request.user:
            post.deleted = True
            post.save()
            Notification.objects.filter(post_from=post).delete()
            return HttpResponse("Success")


@login_required
@logit
def delete_notifications(request):

    if not 'justnum' in request.GET:   
        notifications = Notification.objects.filter(going_to = request.user.get_profile())
        notifications.delete()

    user_profile = request.user.get_profile()
    user_profile.friend_notifications = 0
    user_profile.save()

    return HttpResponse("winning")
    
@logit
def deleteallposts(request):
    if request.user.is_authenticated():
        user = request.user
        #user_profile = user.get_profile()
        posts = ItemForSale.objects.filter(owner=user)
        if posts:
            for post in posts:
                post.delete()
            return render_to_response('message.html', {'message':'Your posts have been deleted.'},context_instance=RequestContext(request))
        else:
            return render_to_response('message.html', {'message':'No posts created by your account found.'},context_instance=RequestContext(request))


@logit
def showpost(request, pid, super_cat):
    post = get_object_or_404(super_cat, pk=pid)
    if post.deleted and not request.user.is_staff:
        data = {}
        data['title'] = 'Item Deleted'
        data['message'] = 'Sorry, this item has been deleted and is no longer viewable.'
        return render_to_response('message.html', data, context_instance=RequestContext(request))

    if request.method == 'POST' and request.user.is_authenticated():
        user = request.user

        if request.GET.get('sr'):   #sr is the id of the comment that the seller is responding to
            rForm = SellerResponseForm(request.POST)
            if rForm.is_valid and request.user == post.owner:
                rcomment = rForm.save(commit = False)
                orig_comment = Comment.objects.get(id = request.GET.get('sr'))
                orig_comment.seller_response = rcomment.seller_response
                orig_comment.save()
                seller_response_signal.send(sender = Comment, instance = orig_comment)  

        else:  #sr is left unset if this post request is being genenrated by the creation of a comment, not a resposne
            cForm = CommentForm(request.POST)
            if cForm.is_valid:
                comment = cForm.save(commit = False)
                comment.sender = user
                comment.item = post
                comment.seller_response = ""
                comment.save()
                if user != post.owner:
                    new_comment_signal.send(sender = Comment, instance = comment) 
                #the signal handeler for this, and the above takes care of adding an appropriate nofitication  
            
        return HttpResponseRedirect(request.path)

    else:
        related_posts = []

        cForm = CommentForm()

        ecks = {'post':post, 'related_posts':related_posts, 'is_bookmarked':False, 'comment_form': cForm}
        image_set = post.get_image_set_urls()
        ecks['image_set'] = image_set
        ecks['image_set_length'] = len(image_set)
    
        relevant_comments = Comment.objects.filter(item = post).order_by('time_created')
        ecks['comments'] = relevant_comments

        if request.user.is_authenticated():
            user_profile = request.user.get_profile()
            bookmarks = user_profile.bookmarks.filter(id = pid)
            if bookmarks:
                ecks['is_bookmarked'] = True
            #if user_profile.facebook_id:
                #ecks['is_facebook'] = True
            if request.user == post.owner:
                ecks['response_form'] = SellerResponseForm()

        try:
            links = request.session['links']
            ecks['links'] = links
        except:
            pass

        if "new" in request.GET and int(request.GET['new']) == 1:
            ecks['new'] = 1
        if "repost" in request.GET:
            ecks['repost'] = True
        if "bump" in request.GET:
            ecks['bump'] = True
        if "postffs" in request.GET:
            ecks['post_ffs'] = int(request.GET['postffs'])
        if post.pending_flag:
            if post.pending_buyer == request.user:
                thread = Thread.objects.filter(owner=request.user, other_person=post.owner, post_id=post.id)
                if thread:
                    ecks['thread'] = thread[0]
            if post.owner == request.user:
                thread = Thread.objects.filter(owner=request.user, other_person=post.pending_buyer, post_id=post.id)
                if thread:
                    ecks['thread'] = thread[0]
        elif post.owner != request.user and request.user.is_authenticated():
            threads = Thread.objects.filter(owner=request.user, post_id=post.id)
            if threads.exists():
                ecks['thread'] = threads[0]
        elif post.owner == request.user:
            threads = Thread.objects.filter(owner=request.user, post_id=post.id, declined=False)
            if threads.exists():
                ecks['offers'] = True
        if '@berkeley.edu' in post.owner.email:
            ecks['seller_is_berkeley'] = True
        ecks['this_is_a_post'] = True
        ecks['reviews'] = ItemReview.objects.filter(seller=post.owner).order_by('-time_created')
        ecks['reviews_avg'] = ItemReview.objects.filter(seller=post.owner).aggregate(Avg('score'))['score__avg']

        ecks.update(csrf(request))
        return render_to_response('showpost.html',ecks,context_instance=RequestContext(request))
 

def showpostIFS(request,pid):
    return showpost(request,pid,ItemForSale)

@login_required
@logit
def modify_post(request):
    if request.method == "GET" and request.user.is_authenticated():
        post_pk = request.GET['post_pk']
        action = request.GET['action']
        post = ItemForSale.objects.get(id = int(post_pk))
        if post.owner == request.user:
            if action == "done":
                #the sale is complete (yay). delete post and redirect to profile page
                post.sold = True
                post.pending_flag = True
                post.sold_date = datetime.datetime.now()
                post.save()
                custom_log_message('user ' + str(request.user.id) + ' sold item :) ' + str(post_pk))
                if post.pending_buyer: #in case if marked sold elsewhere (not on BuyNearMe).
                    sale_complete_signal.send(sender=ItemForSale, instance=post)
                return HttpResponseRedirect("/accounts/profile/selling")

            elif action == "repost":
                #the sald didnt work out, repost the item, and redirect seller
                repost_signal.send(sender=ItemForSale, instance=post, target=post.pending_buyer.get_profile())
                try:
                    # Set threads to declined
                    thread1 = Thread.objects.get(owner=post.owner, other_person=post.pending_buyer, item=post)
                    thread2 = Thread.objects.get(owner=post.pending_buyer, other_person=post.owner, item=post)
                    thread1.declined=True
                    thread1.declined_user = post.pending_buyer
                    thread2.declined=True
                    thread2.declined_user = post.pending_buyer
                    thread1.save()
                    thread2.save()
                except:
                    pass
                post.pending_flag = False
                post.pending_buyer = None
                post.expire_date = datetime.datetime.now()+timedelta(days=90)
                custom_log_message('user ' + str(request.user.id) + ' reposted item :( ' + str(post_pk))
                post.save()
                return HttpResponseRedirect("/"+str(post_pk))
            else:
                return HttpResponse("Invalid Request")

        else:
            return HttpResponse("I can not let you do that, Dave")
    else:
        return HttpResponse("please try again")

@login_required
@logit
def edit_item(request,pid):
    #edits fields of a post model
    #fields to be edited
    # title, price, category, description, images
    item = ItemForSale.objects.get(id = int(pid))
    if item.owner == request.user or request.user.is_staff:
        data = {}
        if request.method == "GET":
            data['item'] = item
            data['categories'] = Category.objects.all()
            image_set = item.get_image_set_urls()
            if image_set == [item.get_category_image_url()]:
                image_set = []
            data['image_set'] = image_set
            return render_to_response('edit_item.html',data,context_instance=RequestContext(request))
        else: #POST
            item.title = request.POST["title"]
            item.body = request.POST["description"]
            item.price = float(request.POST["price"])
            new_category_id = request.POST["category_id"]
            item.category = Category.objects.get(id=int(new_category_id))
            
            num_kept = 3 #number of kept images
            old_images = item.image_set.order_by('id')
            if str(request.POST["image2"]) == "no" :
                num_kept -= 1
                if len(old_images) >= 3:
                    image = old_images[2]
                    image.delete()
            
            if str(request.POST["image1"]) == "no" :
                num_kept -= 1
                if len(old_images) >= 2:
                    image = old_images[1]
                    image.delete()
            
            if str(request.POST["image0"]) == "no" :
                num_kept -= 1
                if len(old_images) >= 1:
                    image = old_images[0]
                    image.delete()
            
            files_list = request.FILES.getlist("images")
            for index, file in enumerate(files_list):
                if num_kept < 3:
                    obj = MultiuploaderImage()
                    image = Image.open(file)
                    rotate_name = "rotate-value" + str(index)
                    obj.image = image_rotate(image, float(request.POST[rotate_name]), str(file))
                    obj.filename=str(file)
                    obj.key_data = obj.key_generate
                    obj.post = item
                    obj.save()
                    num_kept += 1
                else:
                    break
            
            item.reset_thumbnail_url()
            item.save()
            return redirect('/'+str(item.id))
    else:
        message = "You do not own this item. I cannot let you do that Dave."
        return render_to_response('message.html',{'message': message},context_instance=RequestContext(request))

@login_required
@logit
def flag_item(request,pid):
    item = ItemForSale.objects.get(id=pid)
    flag, created = ItemFlag.objects.get_or_create(flagger = request.user, item=item)
    data = {}
    if created == False:
        data['title'] = "Item Flag Failed"
        data['message'] = "It looks like you already flagged this item. Email contact@buynear.me for further assistance."
        return render_to_response('message.html',data,context_instance=RequestContext(request)) 
    
    if request.user.is_staff:
        item.deleted = True 
        item.save()
        owner = item.owner
        op = owner.get_profile()
        op.is_banned = True
        op.save()
        
        #uncomment these if u want to remove everythign from banned dude
        #bad_items = ItemForSale.objects.filter(owner=owner)
        #for bad in bad_items:
            #bad.deleted = True
            #bad.save()
        
        data['title'] = "Item Flagged"
        data['message'] = "Thanks for reporting this item. The item and user have been taken down!"
        return render_to_response('message.html',data,context_instance=RequestContext(request))
    
    #check if more than 3 flags exist, if so send mail to admin
    flagged = ItemFlag.objects.filter(item = item)
    if len(flagged) >= 1: #send mail if non admins flag
        send_mail('Item Flagged 2 Times', 'Item with id '+str(item.id)+'is flagged go take it down. http://buynear.me/'+str(item.id), 'noreply@buynear.me',
        ['contact@buynear.me'], fail_silently=True)
    
    data['title'] = "Item Flagged"
    data['message'] = "Thanks for reporting this item. If enough users report this item, it will be taken down. Please email contact@buynear.me for immediate moderation."
    return render_to_response('message.html',data,context_instance=RequestContext(request))
    
def ajax_delete_comment(request, comment_id):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        comment = Comment.objects.get(id=comment_id)
        if request.user == comment.sender or request.user.is_staff:
            comment.delete()
            return HttpResponse()
    return HttpResponse()
    
def ajax_delete_response(request, comment_id):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        comment = Comment.objects.get(id=comment_id)
        if request.user == comment.item.owner:
            comment.seller_response = ""
            comment.save()
            return HttpResponse()
    return HttpResponse()
    
@login_required
@logit
def ajax_contact_seller(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        send_bnm_message(request)#in utils.py
        # send_mail(post.title+" Response - "+recipient_name, post.body, 'noreply@buynear.me', [recipient.email])
        return HttpResponse("success")

@login_required
def ajax_confirm_purchase(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        change_purchase(request, True) #in utils.py
        return HttpResponse("success")

@login_required
def ajax_decline_purchase(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        change_purchase(request, False)#in utils.py
        return HttpResponse("success")

@login_required
def ajax_undo_decline_purchase(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        recipient_pk = request.POST['recipient_pk']
        post_pk = request.POST['post_pk']

        recipient = User.objects.get(id=int(recipient_pk))
        post = ItemForSale.objects.get(id=int(post_pk))
        sender = request.user

        thread1 = Thread.objects.get(owner=sender, other_person=recipient, item=post, post_title=post.title, post_id=post.id)
        thread2 = Thread.objects.get(owner=recipient, other_person=sender, item=post, post_title=post.title, post_id=post.id)
        thread1.declined = False
        thread2.declined = False
        thread1.save()
        thread2.save()

        send_bnm_message(request)#in utils.py
        return HttpResponse("success")

@logit
def bookmark_post(request):
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        post_pk = int(request.POST["post_pk"])
        if user_profile.bookmarks.filter(pk=post_pk):
            #delete post from bookmarks
            user_profile.bookmarks.remove(post_pk)
        else:
            #add post to bookmarks
            user_profile.bookmarks.add(post_pk)
        return HttpResponse(post_pk,'application/javascript')
  
@logit          
def sendmessage(request, receiver):
    if request.user.is_authenticated():
        user = request.user
        try:
            if request.method == 'POST':
                form = MessageForm(request.POST, sender=user, recipient=receiver)
                if form.is_valid():
                    model = form.save(commit=False)
                    send_mail(model.title+' Response', model.body, 'noreply@buynear.me', [receiver.email])
                    message = "Message sent to their email! They have received a notification as well."
                    return render_to_response('message.html',{'message':message},context_instance=RequestContext(request)) 
                message = "An error occured, please try again."
                return render_to_response('message.html',{'message': message},context_instance=RequestContext(request))
        except:
            message = "An error occured, please try again."
            return render_to_response('message.html',{'message': message},context_instance=RequestContext(request))

'''
def contactsellerIFS(request, pid):
    return contactseller(request, pid, ItemForSale)
'''

@login_required
def user_posts(request):
    if request.user.is_authenticated():
        user = request.user
        #user_profile = user.get_profile()
        posts = ItemForSale.objects.filter(owner=user)
        return render_to_response('user_posts.html',{'posts':posts},context_instance=RequestContext(request))
    raise Http404

def filteritem(request,item):
    filter_ifs = ItemForSale.objects.filter(category__name__exact=item)
    return render_to_response('index.html', {'cc_ifs':filter_ifs},context_instance=RequestContext(request))
    
def filterfurniture(request):
    return filteritem(request,'Furniture')

# Not used???
'''
def search(request):
    """query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'body','category__name','circles__name'])
        found_entries = ItemForSale.objects.filter(entry_query).order_by('-time_created')

    if request.is_ajax():
        data = serializers.serialize('json',found_entries)
        return HttpResponse(data,'application/javascript')"""

    return render_to_response('index.html',{ 'query_string': query_string, 'cc_ifs': found_entries }, context_instance=RequestContext(request))
'''

def boxview(request):
    query_string = ''
    #found_entries = ItemForSale.objects.all()
    found_entries = 1 #This is a dummy value which isnt used at all
    all_cats = Category.objects.order_by('name')
    other_category, created = Category.objects.get_or_create(name='Other')
    return_dict = {'cc_ifs':found_entries,'cc_cats':all_cats,'other_category':other_category}
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        my_public_circles = profile.my_circles.filter(is_public = True)
        my_private_circles = profile.my_circles.filter(is_public = False)
        return_dict['my_private_circles'] = my_private_circles
        return_dict['my_public_circles'] = my_public_circles
        cc_circs = profile.my_circles.all()
    else:
        cc_circs = Circle.objects.filter(is_public=True)
    return_dict['cc_circs'] = cc_circs

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = str(request.GET['q'])
        return_dict['q'] = query_string
    return render_to_response('box.html', return_dict, context_instance=RequestContext(request))


@login_required
def ajax_friend_notifications(request):
    dude = request.user.get_profile()
    
    notifications = Notification.objects.filter(going_to = dude).order_by('-time_created')  

    if 'cap' in request.GET:
        notifications = notifications[:7]
        
    for note in notifications:
        pfrom = note.post_from
        note.title = pfrom.title
        note.username = pfrom.owner.get_full_name()
        note.second_username = ""
        note.num_unread = dude.friend_notifications
        if note.second_party:
            note.second_username = note.second_party.user.get_full_name()

#    dude.friend_notifications = 0
    dude.save()

    data = serializers.serialize('json',notifications, indent = 4, extras = ('num_unread','second_username','username','title',))
    return HttpResponse(data,'application/javascript')
        

def ajax_box(request):
    query_string = ''

    p=0  #what page are we on? (for infinite scroll / pagination, both are same for server)
    if('p' in request.GET) and request.GET['p'].strip():
        try:
            p=int(request.GET['p'])
        except ValueError:
            p=0

    p*=p>0

    # fbf=0
            
    checked_circles = request.GET.getlist('circle')
    checked_categories = request.GET.getlist('category')
    
    min_price = 0
    
    try:
        max_price = float(ItemForSale.objects.aggregate(Max('price'))['price__max']) #
    except TypeError as e: #error occurs if nothing in db and the operand of float returns None
        max_price = 0 
    if ('max_price' in request.GET) and request.GET['max_price'].strip() and float(request.GET['max_price'])>= 0:
        max_price = float(request.GET['max_price'])
    if ('min_price' in request.GET) and request.GET['min_price'].strip() and float(request.GET['min_price'])>= 0:
        min_price = float(request.GET['min_price'])

    # if ('fbf' in request.GET) and request.GET['fbf'].strip() and float(request.GET['fbf'])>= 0:
    #     fbf=1

    checked_circles = map(int,checked_circles)
    checked_categories = map(int, checked_categories)
    #if len(checked_categories) == 11:
    #    checked_categories == range(1, 5) + range(6, 12) #take out Facebook Post Category

    found_entries = SearchQuerySet()

    # friends = []

    # if fbf and request.user.is_authenticated():
    #     friends = FacebookUser.objects.filter(user_id = request.user.id)
    #     friend_ids = [x.facebook_id for x in friends]
    #     found_entries = found_entries.filter(owner_facebook_id__in = friend_ids)

    found_entries = found_entries.filter(
            price__range=(min_price,max_price),
            approved="true",
            sold="false",
            pending_flag="false",
            deleted="false",
            expire_date__gte=datetime.datetime.now()-datetime.timedelta(weeks=300)
        )
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        found_entries = found_entries.filter(
            text=found_entries.query.clean(query_string),
            )

        #found_entries = SearchQuerySet().filter(text=query_string)
        #found_entries = found_entries.filter(entry_query) #auto orders by relevance score

    #haystack bugs if you feed it an empty list so only pass in as filter param when needed
    #client sends empty array if Everything is checked
    if checked_categories:
        found_entries = found_entries.filter(category__in=checked_categories)

    #These values determine the number of boxes in each GET. Keep divisible by 3.
    load_from = 39 * p
    load_to = 39 * (p+1)
    #sorting order. order variable determines what goes first. ex: order=priceLow, cheapest first
    order  = request.GET['order']
    if order == 'dateNew':
        found_entries = found_entries.order_by('-time_created')[load_from:load_to]
    elif order == 'dateOld':
        found_entries = found_entries.order_by('time_created')[load_from:load_to]
    elif order == 'priceLow':
        found_entries = found_entries.order_by('price')[load_from:load_to]
    elif order == 'priceHigh':
        found_entries = found_entries.order_by('-price')[load_from:load_to]

    #is user logged in? highlight his friends' posts
    #TODO: this could be very inefficient. consider performance optimization... perhaps store facebook user id of creator in post model...
    
    # fatty_cheese_wheel = []

    # if request.user.is_authenticated():
    #     user = request.user
    # #    friends = FacebookUser.objects.filter(user_id = user.id)
    #
    #     if fbf and friends:
    #         for search_result in found_entries:
    #             item = search_result.object
    #             item.score = search_result.score
    #             try:
    #                 m8 = friends.get(facebook_id = item.owner_facebook_id)
    #                 item.friend = 1
    #                 item.friendname = m8.name
    #             except:
    #                 item.friend = 0
    #                 item.friendname = ""
    #             item.boxsize = 1
    #
    #             fatty_cheese_wheel.append(search_result.object)
    #
    #          #   if fbf:
    #          #       if search_result.object.friend:
    #          #           fatty_cheese_wheel.append(search_result.object)
    #          #   else:
    #          #       fatty_cheese_wheel.append(search_result.object)
    #     else:
    #         foreveralone(found_entries, fbf, fatty_cheese_wheel)
    # else:
    #     foreveralone(found_entries, fbf, fatty_cheese_wheel)
    #
    #
    # #kludge until someone can get haystack to work
    # #filter out all the pending items for sales, filter out the deleted ones, filter out the already sold ones
    # #fatty_cheese2 = []
    # #for x in fatty_cheese_wheel:
    # #    if not x.sold and not x.pending_flag and not x.deleted:
    # #        fatty_cheese2.append(x)
    # #fatty_cheese_wheel = fatty_cheese2
    #
    #
    #
    # #for x in found_entries:
    # #    if fbf:
    # #        if x.object.friend:
    # #            fatty_cheese_wheel.append(x.object)
    # #    else:
    # #        fatty_cheese_wheel.append(x.object)
    

    # data = serializers.serialize('json', fatty_cheese_wheel , indent = 4, extras=('boxsize','pending_flag','friend','friendname','get_thumbnail_url', 'get_seller_first_name', 'get_seller_profile_picture', 'score'))
    data = serializers.serialize('json', [query.object for query in found_entries] , indent = 4, extras=('get_thumbnail_url', 'get_seller_first_name', 'get_seller_profile_picture'))
    return HttpResponse(data,'application/javascript')

# def foreveralone(found_entries, fbf, fatty_cheese_wheel):
# #    print(found_entries)
#     for item in found_entries:
# #        print("------SWAG"+str(item))
#         item.object.friend = 0
#         item.object.friendname = ""
#         item.object.boxsize = 1
#         item.object.score = item.score
#
#         if fbf:
#             if item.object.friend:
#                 fatty_cheese_wheel.append(item.object)
#         else:
#             fatty_cheese_wheel.append(item.object)
   
class ContactView(TemplateView):
    template_name = 'contact.html'
    
class AboutView(TemplateView):
    template_name = 'about.html'
    
def all_circles(request):
    all = Circle.objects.filter(is_public=True)
    return render_to_response('all_circles.html',{'all':all},context_instance=RequestContext(request))
    
@login_required
@logit
def create_circle(request):
    if request.method == 'POST': 
        form = CircleForm(request.POST, request.FILES)

        if form.is_valid():        
            circle = form.save(commit=False)
            
            if circle.is_public:
                try:
                    Circle.objects.get(name=circle.name)
                    return render_to_response('create_circle.html',{'form':form,'message':"That public group already exists"},context_instance=RequestContext(request))
                except:
                    pass
            
            # see if url_key exists and if does, regenerate one
            while True:
                try:
                    url_key = ""
                    # create a 6 length random key
                    for i in range(0,6):
                        url_key += random.choice(RANDOM_CHARS)
                    c = Circle.objects.get(url_key=url_key)
                except: #circle doesn't exist with key so we good
                   break

            user = request.user

            circle.creator = user;
            circle.url_key = url_key
            circle.save()

            user_profile = user.get_profile()
            user_profile.my_circles.add( circle )
            
            return redirect(circle)
            #return render_to_response('message.html',{'message':'Circle Created!'},context_instance=RequestContext(request))
        else:
            return render_to_response('create_circle.html',{'form':form},context_instance=RequestContext(request))
    else:        
        form = CircleForm()
        data = {'form':form}
        data.update(csrf(request))
        return render_to_response('create_circle.html',data,context_instance=RequestContext(request))
      
  
def view_circle(request,url_key):
    if request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        query = Circle.objects.filter(url_key=url_key)
        if len(query)==0:
            return render_to_response('message.html',{'message':'Circle Not Found'},context_instance=RequestContext(request))
            
        circle = query[0]

        if request.is_ajax():
            action = str(request.GET['action'])
            if action == "Join":
               user_profile.my_circles.add(circle)
            else: #action == "Leave"
               user_profile.my_circles.remove(circle)
            return HttpResponse(action,'application/javascript')        
        
        #check if user has the circle on the profile
        try:
            has_circle = user_profile.my_circles.get(url_key=url_key)
            action = "Leave"
        except: #will error if user doesn't have the circle
            action = "Join"
            
        all_items = ItemForSale.objects.filter(circles__id=circle.id)
        all_cats = Category.objects.all()
        #all_circs = Circle.objects.all()
        all_circs = [circle]
        data = {'circle':circle,'action':action,'all_items':all_items,'cc_cats':all_cats,'cc_circs':all_circs}
        
        return render_to_response('view_circle.html',data,context_instance=RequestContext(request))
        
    else: # for the not logged in loser
        query = Circle.objects.filter(url_key=url_key)
        all_cats = Category.objects.all()
        all_circs = Circle.objects.all()
        if len(query)==0:
            return render_to_response('message.html',{'message':'Circle Not Found'},context_instance=RequestContext(request))
        circle = query[0]
        all_items = ItemForSale.objects.filter(circles__id=circle.id)
        return render_to_response('view_circle.html',{'circle':circle,'cc_cats':all_cats,'action':'None','cc_circs':all_circs,'all_items':all_items},context_instance=RequestContext(request))

        # this is where the user gets authenticated

@logit
def delete_group(request, url_key):
    if request.method == "POST":
        user = request.user
        circle = Circle.objects.get(url_key=url_key)
        if request.is_ajax() and user == circle.creator:
            items = ItemForSale.objects.annotate(count=Count('circles')).filter(circles = circle, count = 1)
            for item in items:
                item.delete()
            circle.delete()
            return HttpResponse("Success")

@logit
def update_group(request, url_key):
    if request.method=="POST":
        user = request.user
        circle = Circle.objects.get(url_key=url_key)
        if request.is_ajax() and user == circle.creator:
            if "newDescription" in request.POST:
                newDescription = request.POST['newDescription']
                circle.description = newDescription
                circle.save()
            return HttpResponse("Success")

@logit
def verify_user(request,auth_key):
    data = {}
    try:
        verif = VerificationEmailID.objects.get(auth_key=auth_key)
        user = verif.user
        user.is_active = True
        user.save()
        verif.delete()
        data['new_user_name'] = user.get_full_name()
        data['title'] = "Account Activated"
        data['message'] = """Thanks %s, activation complete!<br>""" % str(user.first_name) +  """You may now <a href='/accounts/login'>login</a> using your username and password."""
        return render_to_response('message.html',data,context_instance=RequestContext(request))
    except: #something goes wrong, primarily this url doesnt exist
        data['title'] = "Oops! An error has occurred."
        data['message'] = "Oops! It seems that your activation key is invalid.  Please check the url again."
        return render_to_response('message.html',data,context_instance=RequestContext(request))

@logit
def change_email(request,auth_key):
    data = {}
    try:
        verif = VerificationEmailID.objects.get(auth_key=auth_key)
        user = verif.user
        if verif.email:
            user.email = verif.email
            if not user.facebookprofile.facebook_id:
                user.username = verif.email
            user.save()
            verif.delete()
            data['title'] = "Email Changed"
            data['message'] = "Thanks %s, your email has been changed!<br>" % str(user.first_name) + \
                "You will now receive notifications at %s.<br>" % str(user.email) + \
                "Click <a href='/accounts/profile/settings/'>here</a> to change your account settings or <a href='/browse/'>browse now</a>!"
            return render_to_response('message.html', data,context_instance=RequestContext(request))
        else:
            raise Exception
    except: #something goes wrong, primarily this url doesnt exist
        data['title'] = "Oops! An error has occurred."
        data['message'] = """Oops &ndash; it seems that your activation key is invalid.  Please check the url again."""
        return render_to_response('message.html', data,context_instance=RequestContext(request))

@login_required
def change_name(request):
    if request.method == "GET":
        return render_to_response('profile/change_name.html', context_instance=RequestContext(request))
    else:
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        data = {}
        data['title'] = "Change Name"
        data['message'] = "Your name has been changed successfully, "+request.user.get_full_name()+"!"
        return render_to_response("message.html", data, context_instance=RequestContext(request))


@login_required
@logit
def ajax_delete_thread(request):
    if request.method=="POST":
        thread_pk = request.POST['thread_pk']
        thread = Thread.objects.get(id=thread_pk)
        thread.delete()
        return HttpResponse(thread_pk)
        
@login_required
def profile_status(request):
    user = request.user
    posts = ItemForSale.objects.filter(owner=user).order_by('-time_created')
    user_profile = user.get_profile()
    bookmarks = user_profile.bookmarks.all().order_by('-time_created')
    return render_to_response('profile/profile_default.html', 
                            {'posts':posts, 'bookmarks':bookmarks},
                            context_instance=RequestContext(request))

@login_required
def profile_settings(request):
    data = {}
    user_profile = request.user.get_profile()
    if request.method=="POST":
        form = SettingsForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
        data['form'] = form
        data['message'] = True
        return render_to_response('profile/profile_settings.html',data,context_instance=RequestContext(request))
    else:
        form = SettingsForm(instance=user_profile)
        data['form'] = form
        data.update(csrf(request))
        return render_to_response('profile/profile_settings.html',data,context_instance=RequestContext(request))


@login_required
def profile_messages(request):
    data = {}
    user = request.user

    selling_ids = [poast.pk for poast in ItemForSale.objects.filter(owner=user).filter(pending_flag = False).filter(deleted=False)]

    my_threads = Thread.objects.filter(owner=user).filter(post_id__in = selling_ids).order_by('is_read','-newest_message_time')

    for thread in my_threads:
        try:
            ItemForSale.objects.get(id=thread.post_id)
        except:
            thread.post_deleted = True
            thread.save()

    data['my_threads'] = my_threads
    
    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    return render_to_response('profile/profile_messages.html',data,context_instance=RequestContext(request))



@login_required
def profile_selling(request):
    data = {}
    user = request.user

    base_unsold_itemset = ItemForSale.objects.filter(owner=user,
                                                  pending_flag=False, sold=False,
                                                  deleted=False).order_by('-time_created')
    ifs_waiting_list = [item for item in base_unsold_itemset if not item.is_expired]
    expired_items = [item for item in base_unsold_itemset if item.is_expired]

    bought_items = ItemForSale.objects.filter(owner=user, pending_flag=True, sold=False)
    bought_threads_ids = []
    for item in bought_items:
        try: #for some odd reason if .get fails, fail silently
            bought_thread = Thread.objects.get(owner=user, other_person=item.pending_buyer, item=item)
            bought_threads_ids.append(bought_thread.id)
        except:
            pass

    bought_threads = Thread.objects.filter(id__in=bought_threads_ids).order_by('is_read','-newest_message_time')

    pending_threads_ids = []
    for item in base_unsold_itemset:
        pending_threads = Thread.objects.filter(owner=user, item=item, declined=False)
        for thread in pending_threads:
            if thread.item and thread.item.owner == user:
                pending_threads_ids.append(thread.id)
    pending_threads = Thread.objects.filter(id__in=pending_threads_ids).order_by('is_read','-newest_message_time')


    declined_threads_ids = []
    #include declined threads for sold items
    for item in ItemForSale.objects.filter(owner=user, deleted=False).order_by('-time_created'):
        declined_threads = Thread.objects.filter(owner=user, item=item, declined=True)
        for thread in declined_threads:
            if thread.item and thread.item.owner == user:
                declined_threads_ids.append(thread.id)
    declined_threads = Thread.objects.filter(id__in=declined_threads_ids).order_by('is_read','-newest_message_time')

    sold_items = ItemForSale.objects.filter(owner=user, sold=True)
    sold_threads_ids = []
    sold_item_ids = []
    for item in sold_items:
        try:
            sold_thread = Thread.objects.get(owner=user, other_person=item.pending_buyer, item=item)
            sold_threads_ids.append(sold_thread.id)
            sold_item_ids.append(item.id)
        except:
            pass
    sold_threads = Thread.objects.filter(id__in = sold_threads_ids).order_by('is_read','-newest_message_time')

    sold_items_outside = ItemForSale.objects.filter(owner=user, sold=True).exclude(id__in=sold_item_ids)

    data['pending_threads'] = pending_threads         #needs confirmation
    data['my_threads'] = bought_threads               #bought threads
    data['ifs_waiting_list'] = ifs_waiting_list       #unsold
    data['ifs_sold'] = sold_threads                   #sold
    data['sold_outside_list'] = sold_items_outside    #sold outside BNM
    data['ifs_expired'] = expired_items               #expired items
    data['declined_threads'] = declined_threads       #declined purchase requests
    
    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    return render_to_response('profile/profile_selling.html',data,context_instance=RequestContext(request))




@login_required
def profile_buying(request):
    data = {}
    user = request.user

    pending_buying_ids = [x.id for x in ItemForSale.objects.filter(pending_buyer=request.user, pending_flag=True).filter(sold=False)]
    completed_ids = [x.id for x in ItemForSale.objects.filter(pending_buyer=request.user).filter(sold=True)]

    my_threads = Thread.objects.filter(owner=user).filter(post_id__in=pending_buying_ids).order_by('is_read','-newest_message_time','-timestamp')

    completed_threads = Thread.objects.filter(owner=user, post_id__in=completed_ids).order_by('is_read','-newest_message_time','-timestamp')


    pending_threads = Thread.objects.filter(owner=user, declined=False)
    pending_threads_ids = []
    for thread in pending_threads:
        if thread.item and thread.item.pending_flag == False and thread.item.owner != user:
            pending_threads_ids.append(thread.id)
    pending_threads = Thread.objects.filter(id__in=pending_threads_ids).order_by('is_read','-newest_message_time')

    declined_threads = Thread.objects.filter(owner=user, declined=True)
    declined_threads_ids = []
    for thread in declined_threads:
        if thread.item and thread.item.pending_flag == False and thread.item.owner != user:
            declined_threads_ids.append(thread.id)
    declined_threads = Thread.objects.filter(id__in=declined_threads_ids).order_by('is_read','-newest_message_time')

    for thread in my_threads:
        try:
            ItemForSale.objects.get(id=thread.post_id)
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
    data['pending_threads'] = pending_threads
    data['declined_threads'] = declined_threads
    
    user_profile = user.get_profile()
    user_profile.notifications = 0
    user_profile.save()
    return render_to_response('profile/profile_buying.html',data,context_instance=RequestContext(request))

#@login_required(redirect_field_name='/view_thread')
@login_required
def profile_view_thread(request,thread_id):
    thread = Thread.objects.get(id = thread_id)
    if thread.owner != request.user:
        return redirect('/')
    is_owner = False

    poast = 7

    try:
        poast = ItemForSale.objects.get(id=thread.post_id)
        if poast.owner == request.user:
            is_owner = True
    except:
        thread.post_deleted = True  

    thread.is_read = True
    thread.save()

    messages = thread.messages.all().order_by('-time_created')
    data = {"thread":thread, "messages": messages, "is_owner":is_owner, "this_is_a_thread":True}

    if request.user == thread.declined_user:
        data['is_declined_user'] = True

    if not thread.post_deleted:
        data['post'] = poast

    return render_to_response('profile/profile_view_thread.html',data,context_instance=RequestContext(request))

@login_required
def profile_circles(request):
    data = {}
    user = request.user
    user_profile = user.get_profile()
    my_circles = user_profile.my_circles.all().order_by('name')
    my_private_circles = my_circles.filter(is_public=False)
    my_public_circles = my_circles.filter(is_public=True)
    data['my_circles'] = my_circles
    data['my_private_circles'] = my_private_circles
    data['my_public_circles'] = my_public_circles
    data['is_facebook'] = False
    if user_profile.facebook_id:
        data['is_facebook'] = True
    if 'msg' in request.GET:
        data['msg'] = request.GET['msg']
    return render_to_response('profile/profile_circles.html', data, context_instance=RequestContext(request))

@login_required
def profile_reviews(request):
    data = {}
    written_reviews = ItemReview.objects.filter(buyer=request.user).order_by('-time_created')
    reviewed_item_ids = [review.item.id for review in written_reviews]
    not_reviewed_items = ItemForSale.objects.filter(pending_flag=True, pending_buyer=request.user).exclude(id__in = reviewed_item_ids).order_by('-time_created')
    data['written_reviews'] = written_reviews
    data['not_reviewed_items'] = not_reviewed_items
    if "message" in request.GET:
        data['message'] = request.GET['message']
    return render_to_response('profile/profile_reviews.html', data, context_instance=RequestContext(request))

@login_required
@logit
def account_setup(request):
    data = {}
    user = request.user
    user_profile = user.get_profile()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            auth_key = ""
            # create a 20 length random key
            for i in range(0,20):
                auth_key += random.choice(RANDOM_CHARS)

            verif = VerificationEmailID(user=user, auth_key=auth_key, email=email)
            verif.save()
            send_templated_mail(
                template_name='change_email',
                from_email='Buy Near Me <noreply@buynear.me>',
                recipient_list=[email],
                context={
                    'auth_key':auth_key,
                    'first_name':user.first_name
                },
            )

            data['title'] = "Email Verification"
            data['message'] = """Verification email has been sent to your new email address: %s
                <br>Follow the instructions on the email to complete this change.""" % (email)
        else:
            data['title'] = "Email Verification Failed"
            data['message'] = """Verification email has not been sent. Please try again <a href="/account_setup/">here</a>
                <br>or contact us for assistance at
                <a href="mailto:contact@buynear.me?Subject=Email%20Verification%20Failed">
                contact@buynear.me</a>."""
        return render_to_response('message.html', data, context_instance=RequestContext(request))

        #return render_to_response('index.html',context_instance=RequestContext(request) )
    else:
        form = EmailForm()
        data['form'] = form
        user_profile.first_time = False
        user_profile.save()
        return render_to_response('registration/account_setup.html', data, context_instance=RequestContext(request))

def user(request, user_id, review_page=False):
    data = {}
    user = User.objects.get(id=user_id)
    data['user'] = user
    data['user_profile'] = user.get_profile()
    data['items_sold'] = ItemForSale.objects.filter(owner=user,pending_flag=True, sold=True, deleted=False).order_by('-time_created')
    data['items_bought'] = ItemForSale.objects.filter(pending_buyer=user, pending_flag=True, sold=True, deleted=False).order_by('-time_created')
    data['items_listed'] = ItemForSale.objects.filter(owner=user, pending_flag=False, sold=False, deleted=False).order_by('-time_created') #currently listed
    data['reviews'] = ItemReview.objects.filter(seller=user).order_by('-time_created')
    data['reviews_avg'] = ItemReview.objects.filter(seller=user).aggregate(Avg('score'))['score__avg']
    data['review_page'] = review_page #if True, the html will go to the reviews page
    return render_to_response('user.html', data, context_instance=RequestContext(request))

def user_reviews(request, user_id):
    return user(request, user_id, review_page=True)

@login_required
def upload_temp_photo(request):
    if request.method == "POST" and request.is_ajax():
        profile = request.user.get_profile()
        file = request.FILES['temp-photo']
        img = Image.open(file)

        #resize img if too big
        max_height = float(800)
        max_width = float(1200)
        img_width = float(img.size[0])
        img_height = float(img.size[1])
        if img_height > max_height or img_width > max_width:
            ratio = min(max_width/img_width, max_height/img_height)
            new_height = int(ratio*img_height)
            new_width = int(ratio*img_width)
            img = img.resize((new_width,new_height))

        img = image_rotate(img, 0, str(file))
        if profile.temp_image:
            profile.temp_image.delete()
        profile.temp_image = img
        profile.save()
        return HttpResponse(profile.temp_image.url)

@login_required
def upload_profile_photo(request):
    if request.method == "POST" and request.is_ajax():
        profile = request.user.get_profile()
        img = Image.open(profile.temp_image)
        x1 = int(request.POST['x1'])
        y1 = int(request.POST['y1'])
        width = int(request.POST['width'])
        cropped = img.crop((x1, y1, x1 + width, y1+width))
        img = image_rotate(cropped, 0, request.user.username + ".jpg")
        if profile.temp_image:
            profile.temp_image.delete()
        if profile.image:
            profile.image.delete()
        profile.image = img
        profile.save()
        return HttpResponse("Ok")

@login_required
def delete_profile_photo(request):
    if request.method == "POST" and request.is_ajax():
        profile = request.user.get_profile()
        if profile.image:
            profile.image.delete()
        profile.save()
        return HttpResponse("OK")

@login_required
def repost_item(request):
    if request.method == 'POST':
        item = ItemForSale.objects.get(id=request.POST['post_id'])
        if request.user == item.owner:
            expired = item.is_expired
            item.expire_date = datetime.datetime.now()+timedelta(days=90)
            item.time_created = datetime.datetime.now()
            item.save()
            if expired:
                return redirect(item.get_absolute_url()+"?repost=1")
            return redirect(item.get_absolute_url()+"?bump=1")
        else:
            return redirect(item.get_absolute_url())

@login_required
def ajax_repost_item(request):
    if request.method == 'POST':
        item = ItemForSale.objects.get(id=request.POST['post_id'])
        if request.user == item.owner:
            item.expire_date = datetime.datetime.now()+timedelta(days=90)
            item.time_created = datetime.datetime.now()
            item.save()
            return HttpResponse("OK")
        else:
            return HttpResponse("Repost Item Failed")

@login_required
def review_item(request, item_id):
    item = ItemForSale.objects.get(id=item_id)
    if not item.pending_flag or item.pending_buyer != request.user:
        title = "Error"
        msg = "I can't let you do that, Dave. No but seriously, something went wrong. Contact support for further assistance."
        return render_to_response('message.html',{'title':title,'message':msg},context_instance=RequestContext(request))

    data = {}
    if request.method == "GET":
        data['item'] = item
        filter = ItemReview.objects.filter(buyer=request.user, seller=item.owner, item=item)
        if filter:
            review = filter[0]
            data['score'] = review.score
            data['comment'] = review.comment
        return render_to_response('review_item.html', data, context_instance=RequestContext(request))
    else:
        score = request.POST["score"]
        comment = request.POST["comment"]
        filter = ItemReview.objects.filter(buyer=request.user, seller=item.owner, item=item)
        if filter:
            review = filter[0]
            review.score = score
            review.comment = comment
            review.save()
        else:
            review = ItemReview.objects.create(buyer=request.user,
                                               seller=item.owner,
                                               item=item,
                                               score=score,
                                               comment=comment)
        response = redirect('account_reviews')
        response['Location'] += '?message=Your review has been posted.'
        item_reviewed_signal.send(sender = ItemReview, review=review)
        return response
