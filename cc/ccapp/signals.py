
from django_facebook.signals import user_registered
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch.dispatcher import Signal

from ccapp.models import ItemForSale, Notification, Comment, Thread
from django_facebook.models import FacebookUser, FacebookProfile
from templated_email import send_templated_mail


def fb_user_registration_hndlr(sender, **kwargs): #im not sure how to spell handeler right so no vowels



    '''Signaler handeler for...
  ________________
< FACEBOOK ONLY! >
 ----------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

     ...new user registration'''


    newuser = kwargs['user']

    #do crap with the user if needed...    

    return



user_registered.connect(fb_user_registration_hndlr)


post_created_signal = Signal()
new_comment_signal = Signal()
seller_response_signal = Signal()
buy_button_signal = Signal() 
sale_complete_signal = Signal()
repost_signal = Signal()
message_to_seller_signal = Signal()
message_to_buyer_signal = Signal()

#@receiver(post_save, dispatch_uid="AAAAARGH")
def post_save_hndlr(sender, **kwargs):
    '''catch-all handeler for any and all model save() functions'''

    if sender == ItemForSale:
        post = kwargs['instance']
        owner_profile = post.owner.get_profile()    
        friends = FacebookUser.objects.filter(user_id = post.owner.id)
        for friend in friends:
            try:
                dude = FacebookProfile.objects.select_related().get(facebook_id = friend.facebook_id)
                new_note = Notification(post_from = post, going_to = dude, type = 0)
                new_note.save()
                dude.friend_notifications += 1
                dude.save()
                if dude.message_email:
                    send_templated_mail(
                        template_name='item_notification',
                        from_email='noreply@buynear.me',
                        recipient_list=[dude.user.email],
                        context={
                            'recipient_name':dude.get_full_name(),
                            'post':post,
                            'full_name':owner_profile.facebook_name(),
                        },
                    )
            except:
                pass

        x = post.get_thumbnail_set_urls()

    return

post_created_signal.connect(post_save_hndlr, sender=ItemForSale, dispatch_uid="post_post_creating_thingy_aweaerf")


def comment_save_hndlr(sender, **kwargs):
    ''' notify the seller that someone commented '''

    if sender == Comment:
        comment = kwargs['instance']
        item = comment.item
        seller = item.owner.get_profile()
        commenter = comment.sender.get_profile()
        
        new_note = Notification(post_from=item, going_to=seller, type=1)
        new_note.second_party = commenter
        new_note.save()
        seller.friend_notifications += 1
        seller.save()
        if seller.comments_email:
            try:
                send_templated_mail(
                    template_name='user_comment',
                    from_email='noreply@buynear.me',
                    recipient_list=[seller.user.email],
                    context={
                        'message':comment.body,
                        'commenter':commenter.user.get_full_name(),
                        'item':item,
                        'seller':seller.user.get_full_name(),
                        },
                )
            except:
                pass

    return


def seller_response_hndlr(sender, **kwargs):
    ''' notify the commenter that the seller replied '''

    if sender == Comment:
        comment = kwargs['instance']
        item = comment.item
        seller = item.owner.get_profile()
        commenter = comment.sender.get_profile()

        new_note = Notification(post_from = item, going_to = commenter, type = 2)
        new_note.save()
        commenter.friend_notifications += 1
        commenter.save()
        if commenter.replies_email:
            try:
                send_templated_mail(
                    template_name='seller_reply',
                    from_email='noreply@buynear.me',
                    recipient_list=[commenter.user.email],
                    context={
                        'message':comment.body,
                        'commenter':commenter.user.get_full_name(),
                        'item':item,
                        'seller':seller.user.get_full_name(),
                        },
                )
            except:
                pass

    return
 

def buy_button_hndlr(sender, **kwargs):
    ''' notify the seller that someone clicked buy '''

    if sender == ItemForSale:
        item = kwargs['instance']
        message = kwargs['message']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()

        new_note = Notification(post_from = item, going_to = seller, type = 3)
        new_note.second_party = buyer
        new_note.save()
        seller.friend_notifications += 1
        seller.save()
        try:
            send_templated_mail(
                template_name='buy_item',
                from_email='noreply@buynear.me',
                recipient_list=[seller.user.email],
                context={
                    'message':message.body,
                    'buyer':buyer.user.get_full_name(),
                    'item':item,
                    'seller':seller.user.get_full_name(),
                    },
            )
        except:
            pass

    return


def sale_complete_hndlr(sender, **kwargs):
    ''' notify the buyer that the seller has marked the sale complete '''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()
        new_note = Notification(post_from = item, going_to = buyer, type = 4)
        new_note.save()
        buyer.friend_notifications += 1
        buyer.save()

        if buyer.sold_email:
            try:
                send_templated_mail(
                    template_name='sold',
                    from_email='noreply@buynear.me',
                    recipient_list=[buyer.email],
                    context={
                        'post':item,
                        'buyer':buyer.user.get_full_name(),
                        'seller':seller.user.get_full_name()
                    },
                )
            except:
                pass
    return


def item_repost_hndlr(sender, **kwargs):
    ''' notify the buyer that the seller has given up on them, and reposted the item '''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()
        new_note = Notification(post_from = item, going_to = buyer, type = 5)
        new_note.save()
        buyer.friend_notifications += 1
        buyer.save()

        if buyer.failed_to_sell_email:
            try:
                send_templated_mail(
                    template_name='failed_to_sell',
                    from_email='noreply@buynear.me',
                    recipient_list=[buyer.email],
                    context={
                        'post':item,
                        'buyer':buyer.user.get_full_name(),
                        'seller':seller.user.get_full_name()
                    },
                )
            except:
                pass
    return

    
def message_to_seller_hndlr(sender, **kwargs):
    ''''notify the seller that the buyer has sent him a message'''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()
        message = kwargs['message']
        new_note = Notification(post_from = item, going_to = seller, type = 6)
        new_note.second_party = buyer
        thread = Thread.objects.get(owner = seller.user, post_id = item.id)
        new_note.thread_id = thread.id
        new_note.save()
        seller.friend_notifications += 1
        seller.save()

        if seller.message_email:
            try:
                send_templated_mail(
                    template_name='message',
                    from_email='noreply@buynear.me',
                    recipient_list=[seller.email],
                    context={
                        'message':message.body,
                        'post':item,
                        'sender':buyer.user.get_full_name(),
                        'target':seller.user.get_full_name(),
                        'thread':thread
                        },
                )
            except:
                pass

    return


def message_to_buyer_hndlr(sender, **kwargs):
    ''''notify the seller that the buyer has sent him a message'''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()
        message = kwargs['message']
        new_note = Notification(post_from = item, going_to = buyer, type = 7)
        thread = Thread.objects.get(owner = buyer.user, post_id = item.id)
        new_note.thread_id = thread.id
        new_note.save()
        buyer.friend_notifications += 1
        buyer.save()

        if buyer.message_email:
            send_templated_mail(
                template_name='message',
                from_email='noreply@buynear.me',
                recipient_list=[buyer.email],
                context={
                    'message':message.body,
                    'post':item,
                    'sender':seller.user.get_full_name(),
                    'target':buyer.user.get_full_name(),
                    'thread':thread
                    },
            )
    return


new_comment_signal.connect(comment_save_hndlr, sender = Comment, dispatch_uid = "yolo")
seller_response_signal.connect(seller_response_hndlr, sender = Comment, dispatch_uid = "99xp")
buy_button_signal.connect(buy_button_hndlr, sender = ItemForSale, dispatch_uid = "11")
sale_complete_signal.connect(sale_complete_hndlr, sender = ItemForSale, dispatch_uid = "123")
repost_signal.connect(item_repost_hndlr, sender = ItemForSale, dispatch_uid = "333")
message_to_seller_signal.connect(message_to_seller_hndlr, sender = ItemForSale, dispatch_uid = "234")
message_to_buyer_signal.connect(message_to_buyer_hndlr, sender = ItemForSale, dispatch_uid = "woodchip")

