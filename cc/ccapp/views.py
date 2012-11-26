from ccapp.models import *
from ccapp.signals import post_created_signal

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core import serializers
from django.db.models import Avg, Max, Min, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic import TemplateView
#from django.utils import simplejson

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

@csrf_exempt
def canvas(request):
    return render_to_response('canvas.html', context_instance = RequestContext(request))

def note(request):
    title = request.GET['title']
    msg = request.GET['msg']
    return render_to_response('message.html',{'title':title,'message':msg},context_instance=RequestContext(request))


def ajax_circle_search(request): 
    if request.is_ajax() or True:
        results = Circle.objects.filter(is_public=True)
        
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


def friendslist(request):
    #try:
    graph = get_facebook_graph(request)
    #print(graph)
    facebook = FacebookUserConverter(graph)
    #print(facebook)
    print(dir(facebook))
    groups = facebook.get_groups()
    friends = facebook.get_friends()
    likes = facebook.get_likes()
    #store_likes = facebook.get_and_store_likes(request.user)
    print(groups)
    #print(store_likes)
    #print(queryset)
    context_object_name = 'my_friends_list'
    template_name = "friendslist.html" 
    #except OpenFacebookException as e:
    #    print(e)
    #except:
    #    raise Http404
    return render_to_response('friendslist.html',{'my_friends_list': friends, 'my_groups': groups}, context_instance=RequestContext(request))

"""@login_required
def friends(request):
    if request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        if request.method == 'POST':
            form = friendsForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                send
        else:
            form = friendsForm()
            ecks = {'form':form}
            ecks.update(csrf(request))
            return render_to_response('friends.html',ecks, context_instance=RequestContext(request))"""
    
class FriendsView(TemplateView):
    template_name = 'friends.html'

import random

class MainView(TemplateView):
    template_name = 'index.html'

def confirmview(request,pid,secret,super_cat):
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
    confirmview(request,pid,secret,ItemForSale)


def createlistingview(request, super_cat_form, super_cat_model,**kwargs):
    if request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        if request.method == 'POST':
            #try:
             #   model_instance = request.session['instance']
            #except:
            #    model_instance = None
            form = super_cat_form(request.POST, request.FILES)#, instance=model_instance)
            if form.is_valid():
                model = form.save(commit=False)
                #model.is_confirmed = True
                #model.pk = request.POST[u'post_pk']
                model.owner = user

                #MULTIUPLOADER
                #images = MultiuploaderImage.objects.filter(post_key_data=model.key_data)

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
                circleIDs = request.POST.getlist('circles')
                circleQuery = Circle.objects.filter(id__in=circleIDs)
                model.circles = circleQuery
                model.save()

                #MULTIUPLOADER
                #for image in images:
                #    image.post = model
                #    image.save()

                post_created_signal.send(sender = ItemForSale, instance = model)

                return redirect(model)

            else:
                return render_to_response('createlisting.html',{'form':form},context_instance=RequestContext(request))
        else:
            #MULTIUPLOADER COMMENTS
            #model = super_cat_model()
            #model.key_data = model.key_generate

            #form variable gets rewritten in 'if' statement if its within circle
            form = super_cat_form()#instance=model)
            form.fields['circles'].queryset = user_profile.my_circles.all()
            form.fields['circles'].label = "Groups"
            form.fields['circles'].help_text = """Tip: Hold down "Control", or "Command" on a Mac, to select more than one.
                <br>Specify which groups you want to sell to."""


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

            ecks.update(csrf(request))
            return render_to_response('createlisting.html',ecks,context_instance=RequestContext(request))
        
@login_required
def createlistingviewIFS(request):
    return createlistingview(request,ItemForSaleForm,ItemForSale)
    
#def createIFSwithinCircle(request, url_key):
#    return createlistingview(request,ItemForSaleForm,ItemForSale,url_key=url_key)

@login_required
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
def ajax_delete_post(request):
    if request.method == "POST" and request.is_ajax():
        post_id = request.POST['post_id']
        post = ItemForSale.objects.get(pk=post_id)
        if post.owner == request.user:
            post.delete()
            return HttpResponse("Success")

    
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

def showpost(request,pid,super_cat):
 #   try:
    post = super_cat.objects.get(pk=pid)
    related_posts = []
    # category_posts = super_cat.objects.filter(category=post.category).exclude(id=pid)
    # cat_length = len(category_posts)
    # if cat_length>=4:
        # while len(related_posts)<4:
            # rand_post = random.choice(category_posts)
            # if rand_post not in related_posts:
                # related_posts.append(rand_post)
    # else:
        # while len(related_posts)<cat_length:
            # rand_post = random.choice(category_posts)
            # if rand_post not in related_posts:
                # related_posts.append(rand_post)
    form = MessageForm()
    #ecks = {'MsgForm':form, 'post':post, 'related_posts':related_posts}
    ecks = {'post':post, 'related_posts':related_posts, 'is_bookmarked':False}
    image_set = post.get_image_set_urls()
    ecks['image_set'] = image_set
    ecks['image_set_length'] = len(image_set)
    if request.user.is_authenticated():
        user_profile = request.user.get_profile()
        bookmarks = user_profile.bookmarks.filter(id = pid)
        if bookmarks:
            ecks['is_bookmarked'] = True
    ecks.update(csrf(request))
    return render_to_response('postview.html',ecks,context_instance=RequestContext(request))
  #  except:
        #return render_to_response('message.html',{'message':'Oh No! Post does not exist!'},context_instance=RequestContext(request))

def showpostIFS(request,pid):
    return showpost(request,pid,ItemForSale)

@login_required
def ajax_contact_seller(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_authenticated():
        body = request.POST['message']
        recipient_pk = request.POST['recipient_pk']
        post_pk = request.POST['post_pk']
        post = ItemForSale.objects.get(id=int(post_pk))
        sender = request.user
        recipient = User.objects.get(id=int(recipient_pk))
        
        message = Message()
        message.body = body
        message.post_title = post.title
        message.sender = sender
        message.recipient = recipient
        message.save()
        
        #Create 2 Threads for both ends
        try: #see if thread exists, if not create it
            thread1 = Thread.objects.get(owner=sender,other_person=recipient,post_title=post.title,post_id =post_pk)
        except:
            thread1 = Thread.objects.create(owner=sender,other_person=recipient,post_title=post.title,post_id =post_pk)
            
        try: #see if thread exists, if not create it
            thread2 = Thread.objects.get(owner=recipient,other_person=sender,post_title=post.title,post_id =post_pk)
        except:
            thread2 = Thread.objects.create(owner=recipient,other_person=sender,post_title=post.title,post_id =post_pk)
        
        thread1.messages.add(message)
        thread2.messages.add(message)
        thread1.newest_message_time = message.time_created
        thread2.newest_message_time = message.time_created
        thread2.is_read = False
        thread1.save()
        thread2.save()
        
        rec_profile = recipient.get_profile()
        rec_profile.notifications += 1
        rec_profile.save()
        recipient_name = recipient.get_full_name()
        if rec_profile.message_email:
            send_templated_mail(
                template_name='message',
                from_email='noreply@buynear.me',
                recipient_list=[recipient.email],
                context={
                    'message':message.body,
                    'thread':thread2,
                    'post':post,
                    'username':sender.username,
                    'first_name':sender.first_name,
                    'full_name':sender.get_full_name(),
                },
            )
        # send_mail(post.title+" Response - "+recipient_name, post.body, 'noreply@buynear.me', [recipient.email])
        return HttpResponse("success")

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
            
def sendmessage(request, receiver):
    if request.user.is_authenticated():
        user = request.user
        try:
            if request.method == 'POST':
                form = MessageForm(request.POST, sender=user, recipient=receiver)
                if form.is_valid():
                    model = form.save(commit=False)
                    send_mail(post.title+' Response', model.body, 'noreply@buynear.me', [receiver.email])
                    message = "Message sent to their email! They have received a notification as well."
                    return render_to_response('message.html',{'message':message},context_instance=RequestContext(request)) 
                message = "An error occured, please try again."
                return render_to_response('message.html',{'message': message},context_instance=RequestContext(request))
        except:
            message = "An error occured, please try again."
            return render_to_response('message.html',{'message': message},context_instance=RequestContext(request))

def contactsellerIFS(request, pid):
    return contactseller(request, pid, ItemForSale)
                
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

def boxview(request):

    query_string = ''
    #found_entries = ItemForSale.objects.all()
    found_entries = 1 #This is a dummy value which isnt used at all
    all_cats = Category.objects.all().order_by('name')
    other_category, created = Category.objects.get_or_create(name="Other")
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
    return render_to_response('box.html', return_dict ,context_instance=RequestContext(request))

@login_required
def ajax_friend_notifications(request):
    dude = request.user.get_profile()
    notifications = Notification.objects.filter(going_to = dude)
    for note in notifications:
        pfrom = note.post_from
        note.title = pfrom.title
        note.username = pfrom.owner.username
    data = serializers.serialize('json',notifications, indent = 4, extras = ('username','title',))
    notifications.delete()
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
            
    checked_circles = request.GET.getlist('circle')
    checked_categories = request.GET.getlist('category')
    
    min_price = 0
    max_price = float(ItemForSale.objects.aggregate(Max('price'))['price__max'])
    if ('max_price' in request.GET) and request.GET['max_price'].strip() and float(request.GET['max_price'])>= 0:
        max_price = float(request.GET['max_price'])
    if ('min_price' in request.GET) and request.GET['min_price'].strip() and float(request.GET['min_price'])>= 0:
        min_price = float(request.GET['min_price'])

    checked_circles = map(int,checked_circles)
    checked_categories = map(int, checked_categories)

    found_entries = SearchQuerySet().filter(circles__in=checked_circles,category__in=checked_categories,price__range=(min_price,max_price))
    
    """ #OLD NON-HAYSTACK SEARCH
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'body','category__name','circles__name'])
        found_entries = found_entries.filter(entry_query).order_by('-time_created')
    """

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        found_entries = found_entries.filter(text=query_string)
        #found_entries = SearchQuerySet().filter(text=query_string)
        #found_entries = found_entries.filter(entry_query) #auto orders by relevance score

    found_entries = found_entries[(100*p):(100*(p+1))]


    #is user logged in? highlight his friends' posts
    #TODO: this could be very inefficient. consider performance optimization... perhaps store facebook user id of creator in post model...

    def foreveralone():
        for item in found_entries:
            item.object.friend = 0
            item.object.friendname = ""
            item.object.boxsize = random.randint(0,1)
            item.object.score = item.score

    if request.user.is_authenticated(): 
        user = request.user
        friends = FacebookUser.objects.filter(user_id = user.id)
        if friends:
            for search_result in found_entries:
                item = search_result.object
                item.score = search_result.score
                try:
                    op = item.owner.get_profile()
                    ownerid = op.facebook_id 
                    friends.get(facebook_id = ownerid)
                    item.friend = 1
                    item.friendname = op.facebook_name
                except:
                    item.friend = 0
                    item.friendname = ""
                item.boxsize = random.randint(0,1)
        else:
            foreveralone()
    else:
        foreveralone()

    #for x in found_entries:
    #    x.object.score = x.score

    data = serializers.serialize('json', [x.object for x in found_entries] , indent = 4, extras=('boxsize','friend','friendname','get_thumbnail_url','score'))
    return HttpResponse(data,'application/javascript')
   
class ContactView(TemplateView):
    template_name = 'contact.html'
    
class AboutView(TemplateView):
    template_name = 'about.html'
    
def all_circles(request):
    all = Circle.objects.filter(is_public=True)
    return render_to_response('all_circles.html',{'all':all},context_instance=RequestContext(request))
    
@login_required
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

def verify_user(request,auth_key):
    data = {}
    try:
        verif = VerificationEmailID.objects.get(auth_key=auth_key)
        user = verif.user
        user.is_active = True
        user.save()
        verif.delete()
        data['title'] = "Account Activated"
        data['message'] = """Thanks %s, activation complete!<br>""" % str(user.first_name) +  """You may now <a href='/accounts/login'>login</a> using your username and password.""" 
        return render_to_response('message.html',data,context_instance=RequestContext(request))
    except: #something goes wrong, primarily this url doesnt exist
        data['title'] = "Oops! An error has occurred."
        data['message'] = """Oops &ndash; it seems that your activation key is invalid.  Please check the url again."""
        return render_to_response('message.html',data,context_instance=RequestContext(request))

@login_required
def ajax_delete_thread(request):
    if request.method=="POST":
        thread_pk = request.POST['thread_pk']
        thread = Thread.objects.get(id=thread_pk)
        thread.delete()
        return HttpResponse(thread_pk)
        
@login_required
def profile_status(request):
    return redirect('account_posts')
                            
@login_required
def profile_posts(request):
    user = request.user
    posts = ItemForSale.objects.filter(owner=user).order_by('-time_created')
    user_profile = user.get_profile()
    bookmarks = user_profile.bookmarks.all().order_by('-time_created')
    return render_to_response('profile/profile_posts.html', 
                            {'posts':posts, 'bookmarks':bookmarks},
                            context_instance=RequestContext(request))

@login_required
def profile_settings(request):
    if request.method=="POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            form.save()
        return render_to_response('profile/profile_settings.html',data,context_instance=RequestContext(request))
    else:
        data = {}
        user_profile = request.user.get_profile()
        form = SettingsForm(instance=user_profile)
        data['form'] = form
        data.update(csrf(request))
        return render_to_response('profile/profile_settings.html',data,context_instance=RequestContext(request))

@login_required
def profile_messages(request):
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
    return render_to_response('profile/profile_messages.html',data,context_instance=RequestContext(request))

    
@login_required
def profile_view_thread(request,thread_id):
    thread = Thread.objects.get(id = thread_id)
    
    try:
        ItemForSale.objects.get(id=thread.post_id)
    except:
        thread.post_deleted = True
    
    messages = thread.messages.all().order_by('-time_created')
    data = {"thread":thread, "messages": messages}
    thread.is_read = True
    thread.save()
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
    return render_to_response('profile/profile_circles.html',
                             data,
                             context_instance=RequestContext(request))

