from ccapp.models import *
from cc.swamp_logging import logit, custom_log_message
from urlparse import urlparse, parse_qs
from django.db import connection
from cc.ccapp.signals import *
from django.http import HttpResponse, Http404, HttpResponseRedirect

import datetime

#from templated_email import send_templated_mail

from cc.django_facebook.models import *
from cc.django_facebook.decorators import facebook_required, facebook_required_lazy
from cc.django_facebook.api import get_facebook_graph, get_persistent_graph, require_persistent_graph, FacebookUserConverter
from cc.open_facebook.exceptions import OpenFacebookException

#for image rotate
from StringIO import StringIO
from PIL import Image
from PIL import ImageDraw
from PIL.ExifTags import TAGS
from django.core.files.uploadedfile import InMemoryUploadedFile
#

def send_bnm_message(request):
    body = request.POST['message']
    recipient_pk = request.POST['recipient_pk']
    post_pk = request.POST['post_pk']
    post = ItemForSale.objects.get(id=int(post_pk))
    sender = request.user
    recipient = User.objects.get(id=int(recipient_pk))
    first_message = False
    
    if post.pending_flag:
        if request.user not in [post.owner, post.pending_buyer]:
            return HttpResponse("crap " + request.user.username + post.owner.username + post.pending_buyer.username)
            #crap someone else got it before you, sorrym8

    else:
        first_message = True
        post.pending_buyer = request.user
        post.pending_flag = True
        post.save()
        custom_log_message("user " + str(request.user.id) + " bought item " + str(post_pk))
    
    
    message = Message()
    message.body = body
    message.post_title = post.title
    message.sender = sender
    message.recipient = recipient
    message.save()

          

    #Create 2 Threads for both ends
    try: #see if thread exists, if not create it
        thread1 = Thread.objects.get(owner=sender, other_person=recipient, item=post, post_title=post.title, post_id=post.id)
    except:
        thread1 = Thread.objects.create(owner=sender, other_person=recipient, item=post, post_title=post.title, post_id=post.id)
        
    try: #see if thread exists, if not create it
        thread2 = Thread.objects.get(owner=recipient, other_person=sender, item=post, post_title=post.title, post_id=post.id)
    except:
        thread2 = Thread.objects.create(owner=recipient, other_person=sender, item=post, post_title=post.title, post_id=post.id)

    if first_message:
        buy_button_signal.send(sender=ItemForSale, instance=post, message=message)

    else:
        if request.user == post.owner: #sending a message to a buyer
            message_to_buyer_signal.send(sender=ItemForSale, instance=post, message=message)
        else:   #sending a message to a seller
            message_to_seller_signal.send(sender=ItemForSale, instance=post, message=message)

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


def save_fb_items_to_model(facebook, items):
    """
    graph = get_facebook_graph(request)
    facebook = FacebookUserConverter(graph)
    items = JSON array of items from FB API

    Save Facebook items to FacebookPostForExcel
    """

    new_items = []
    existing_items = FacebookPostForExcel.objects.all()
    for item in items:
        try:
            item_id = item.get('id').split('_')[1]
            current_item = existing_items.filter(facebook_id=item_id)
            item_exists = current_item.exists()
            updated_time_string = item.get('updated_time')
            updated_time = None
            if updated_time_string:
                updated_time = datetime.datetime.strptime(
                    item['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
        except:
            continue
        if not item_exists:
            message = item.get('message')
            user_id = item.get('from').get('id')
            seller_name = item.get('from').get('name')
            post_url = item.get('actions')[0].get('link')
            thumbnail_url = item.get('picture')
            picture_url = None
            comments = item.get('comments')
            likes = item.get('likes')
            num_comments = num_likes = 0

            if thumbnail_url:
                try:
                    link = item.get('link')
                    fb_id = parse_qs(urlparse(link).query)['fbid'][0]
                    picture = facebook.get_facebook_url(fb_id)
                    picture_url = picture.get('source')
                except:
                    pass
            if not message:
                continue

            price = 0
            price_string = message.split('$')
            if len(price_string)>1:
                try:
                    price = (float)(re.findall(r"[-+]?\d*\.\d+|\d+", price_string[1])[0])
                except IndexError:
                    pass

            if comments:
                try:
                    num_comments = len(comments.get('data'))
                except:
                    pass
            if likes:
                num_likes = likes.get('count')
            new_item = FacebookPostForExcel(
                        message=message,
                        user_id=user_id,
                        facebook_id=item_id,
                        seller_name=seller_name,
                        num_comments=num_comments,
                        num_likes=num_likes,
                        post_url=post_url,
                        thumbnail_url=thumbnail_url,
                        picture_url=picture_url,
                        price=price,
                        updated_time=updated_time)
            new_items.append(new_item)
        elif not current_item[0].updated_time or current_item[0].updated_time < updated_time: # current_item[0] guaranteed cuz item_exists
            existing_item = current_item[0]
            comments = item.get('comments')
            likes = item.get('likes')
            num_comments = num_likes = 0
            if comments:
                try:
                    num_comments = len(comments.get('data'))
                except:
                    pass
            if likes:
                num_likes = likes.get('count')
            existing_item.num_likes = num_likes
            existing_item.num_comments = num_comments
            existing_item.updated_time = updated_time
            existing_item.save()
    try:
        FacebookPostForExcel.objects.bulk_create(new_items)
    except:
        connection._rollback()
    return new_items


@facebook_required_lazy(scope='publish_actions')
def free_for_sale_post(request, item):
    graph = require_persistent_graph(request)
    if graph.is_authenticated():
        facebook = FacebookUserConverter(graph)
        response = facebook.set_free_for_sale(item)
        return response
    return None


@facebook_required_lazy(scope='publish_actions')
def fb_group_post(request, item, fb_group):
    '''

    :param request:
    :param item: ItemForSale Model
    :param fb_group: URL of group, e.g. '1223124/feed/'
    :return: response if successful

#   try:
    import urllib2
    code = urllib2.urlopen('https://www.facebook.com/dialog/oauth?client_id='+
                           settings.FACEBOOK_APP_ID + '&redirect_uri='+
                           settings.FACEBOOK_REDIRECT_URI + '&scope=read_stream')
    f = urllib2.urlopen('https://graph.facebook.com/oauth/access_token?client_id='+
                        settings.FACEBOOK_APP_ID + '&client_secret=' + settings.FACEBOOK_APP_SECRET +
                        '&grant_type=client_credentials')

    data = f.read()
    print(data) # access_token=171685159547122|he8_Dw5MqyosrndHcDal9t588UQ
    access_token = data.split('|')[0].lstrip('access_token=')
    test = urllib2.urlopen(settings.FACEBOOK_REDIRECT_URI)
    from open_facebook.api import FacebookAuthorization
    token_response = FacebookAuthorization.convert_code(
        code, redirect_uri=redirect_uri)
    expires = token_response.get('expires')
    access_token = token_response['access_token']
    from django_facebook.connect import connect_user
    action, user = connect_user(request)'''

    graph = require_persistent_graph(request)
    if graph.is_authenticated():
        facebook = FacebookUserConverter(graph)
        response = facebook.set_fb_group(item, fb_group)
        return response
    return None
#    except:
#        return None

def image_rotate(image, degrees, filename):  #Rotate a PIL Image, then convert it into a Django file
    im = image.rotate(degrees)
    buffer = StringIO()
    im.save(buffer, "PNG")
    image_file = InMemoryUploadedFile(buffer, None, filename, 'image/png', buffer.len, None)
    return image_file


 
def get_exif(img):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print 'IOERROR ' + fname
    return ret
    