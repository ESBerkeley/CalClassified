
from django_facebook.signals import user_registered
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch.dispatcher import Signal

from ccapp.models import ItemForSale, Notification, Comment, Thread, ItemReview
from django_facebook.models import FacebookUser, FacebookProfile

from ccapp.tasks import *

from datetime import datetime

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
confirm_purchase_signal = Signal()
decline_buyer_purchase_signal = Signal()
decline_seller_purchase_signal = Signal()
item_reviewed_signal = Signal()

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
                dude_full_name = dude.user.get_full_name()
                '''if dude.friend_email:
                    send_email_task.delay(
                        template_name='item_notification',
                        from_email='BuyNearMe <noreply@buynear.me>',
                        recipient_list=[add_name_to_email(dude_full_name, dude.user.email)],
                        context={
                            'recipient_name':dude_full_name,
                            'post':post.id,
                            'full_name':owner_profile.facebook_name(),
                        },
                    )'''
            except:
                pass

        x = post.get_thumbnail_set_urls()

    return

post_created_signal.connect(post_save_hndlr, sender=ItemForSale, dispatch_uid="post_post_creating_thingy_aweaerf")

def add_name_to_email(name, email):
    """
    Returns "INSERT NAME" <INSERT EMAIL>
    formatting
    """
    return '"' + name + '"' + ' <' + email + '>'

def comment_save_hndlr(sender, **kwargs):
    ''' notify the seller that someone commented '''

    if sender == Comment:
        comment = kwargs['instance']
        item = comment.item
        seller = item.owner.get_profile()
        commenter = comment.sender.get_profile()
        if seller != commenter: #if you comment on your own item, dont notify
            new_note = Notification(post_from=item, going_to=seller, type=1)
            new_note.second_party = commenter
            new_note.save()
            seller.friend_notifications += 1
            seller.save()
            seller_full_name = seller.user.get_full_name()
            if seller.comments_email:
                try:
                    send_email_task.delay(
                        template_name='user_comment',
                        from_email='BuyNearMe <noreply@buynear.me>',
                        recipient_list=[add_name_to_email(seller_full_name, seller.user.email)],
                        context={
                            'message':comment.body,
                            'commenter':commenter.user.get_full_name(),
                            'post':item.id,
                            'seller':seller_full_name,
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
        commenter_full_name = commenter.user.get_full_name()
        if commenter.replies_email:
            try:
                send_email_task.delay(
                    template_name='seller_reply',
                    from_email='BuyNearMe <noreply@buynear.me>',
                    recipient_list=[add_name_to_email(commenter_full_name, commenter.user.email)],
                    context={
                        'message':comment.body,
                        'commenter':commenter_full_name,
                        'post':item.id,
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
        buyer = kwargs['buyer'].get_profile()
        new_note = Notification(post_from = item, going_to = seller, type = 3)
        new_note.second_party = buyer

        item.num_interested_buyers += 1
        if not item.first_interested_buy_date:
            item.first_interested_buy_date = datetime.now()
        item.save()

        seller.friend_notifications += 1
        seller.save()
        thread = Thread.objects.get(owner=seller.user, post_id=item.id, other_person=buyer.user)
        new_note.thread_id = thread.id
        new_note.save()

        seller_full_name = seller.user.get_full_name()
        try:
            send_email_task.delay(
                template_name='buy_item',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(seller_full_name, seller.user.email)],
                context={
                    'message':message.body,
                    'buyer':buyer.user.get_full_name(),
                    'post':item.id,
                    'seller':seller_full_name,
                    'thread':thread.id
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
        buyer_full_name = buyer.user.get_full_name()

        thread = Thread.objects.get(owner=buyer.user, post_id=item.id, other_person=seller.user)

        if buyer.sold_email:
            try:
                send_email_task.delay(
                    template_name='sold',
                    from_email='BuyNearMe <noreply@buynear.me>',
                    recipient_list=[add_name_to_email(buyer_full_name, buyer.user.email)],
                    context={
                        'post':item.id,
                        'buyer':buyer_full_name,
                        'seller':seller.user.get_full_name(),
                        'thread':thread.id
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
        buyer_full_name = buyer.user.get_full_name()

        if buyer.failed_to_sell_email:
            try:
                send_email_task.delay(
                    template_name='failed_to_sell',
                    from_email='BuyNearMe <noreply@buynear.me>',
                    recipient_list=[add_name_to_email(buyer_full_name, buyer.user.email)],
                    context={
                        'post':item.id,
                        'buyer':buyer_full_name,
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
        message = kwargs['message']
        buyer_user = kwargs['buyer']

        seller = item.owner.get_profile()
        buyer = buyer_user.get_profile()
        new_note = Notification(post_from=item, going_to=seller, type=6)
        new_note.second_party = buyer
        thread = Thread.objects.get(owner=seller.user, post_id=item.id, other_person=buyer.user)
        new_note.thread_id = thread.id
        new_note.save()
        seller.friend_notifications += 1
        seller.save()
        seller_full_name = seller.user.get_full_name()

        if seller.message_email:
            try:
                send_email_task.delay(
                    template_name='message',
                    from_email='BuyNearMe <noreply@buynear.me>',
                    recipient_list=[add_name_to_email(seller_full_name,seller.user.email)],
                    context={
                        'message':message.body,
                        'post':item.id,
                        'sender':buyer.user.get_full_name(),
                        'recipient':seller_full_name,
                        'thread':thread.id
                        },
                )
            except:
                pass

    return


def message_to_buyer_hndlr(sender, **kwargs):
    ''''notify the buyer that the seller has sent him a message'''
    if sender == ItemForSale:
        item = kwargs['instance']
        buyer_user = kwargs['buyer']
        message = kwargs['message']

        seller = item.owner.get_profile()
        buyer = buyer_user.get_profile()
        new_note = Notification(post_from=item, going_to=buyer, type=7)
        new_note.second_party = seller
        thread = Thread.objects.get(owner=buyer.user, post_id=item.id, other_person=seller.user)
        new_note.thread_id = thread.id
        new_note.save()
        buyer.friend_notifications += 1
        buyer.save()
        buyer_full_name = buyer.user.get_full_name()

        if buyer.message_email:
            send_email_task.delay(
                template_name='message',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(buyer_full_name, buyer.user.email)],
                context={
                    'message':message.body,
                    'post':item.id,
                    'sender':seller.user.get_full_name(),
                    'recipient':buyer_full_name,
                    'thread':thread.id
                    },
            )
    return

def confirm_purchase_hndlr(sender, **kwargs):
    ''''notify the buyer that the seller has confirmed his purchase'''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = item.pending_buyer.get_profile()
        message = kwargs['message']
        new_note = Notification(post_from=item, going_to=buyer, type=8)
        new_note.second_party = seller
        thread = Thread.objects.get(owner=buyer.user, post_id=item.id, other_person=seller.user)
        new_note.thread_id = thread.id
        new_note.save()
        buyer.friend_notifications += 1
        buyer.save()
        buyer_full_name = buyer.user.get_full_name()

        if buyer.message_email:
            send_email_task.delay(
                template_name='confirm',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(buyer_full_name, buyer.user.email)],
                context={
                    'message':message.body,
                    'post':item.id,
                    'sender':seller.user.get_full_name(),
                    'recipient':buyer_full_name,
                    'thread':thread.id
                    },
            )
    return

def decline_seller_purchase_hndlr(sender, **kwargs):
    ''''notify the seller that the buyer has declined his purchase request'''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller = item.owner.get_profile()
        buyer = kwargs['buyer'].get_profile()
        message = kwargs['message']
        new_note = Notification(post_from=item, going_to=seller, type=9)
        new_note.second_party = buyer
        thread = Thread.objects.get(owner=seller.user, post_id=item.id, other_person=buyer.user)
        new_note.thread_id = thread.id
        new_note.save()
        seller.friend_notifications += 1
        seller.save()
        seller_full_name = seller.user.get_full_name()

        if seller.message_email:
            send_email_task.delay(
                template_name='decline_seller',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(seller_full_name, seller.user.email)],
                context={
                    'message':message.body,
                    'post':item.id,
                    'sender':buyer.user.get_full_name(),
                    'recipient':seller_full_name,
                    'thread':thread.id
                    },
            )
    return

def item_reviewed_handler(sender, **kwargs):
    """SIGNAL 10- notify the seller that the buyer has reviewed their item"""
    if sender == ItemReview:
        review = kwargs['review']
        item = review.item
        buyer_profile = review.buyer.get_profile()
        seller_profile = review.seller.get_profile()
        notification = Notification(post_from=item, going_to=seller_profile, type=10, second_party=buyer_profile)
        notification.save()
        seller_profile.friend_notifications += 1
        seller_profile.save()
        if seller_profile.message_email:
            send_email_task.delay(
                template_name='item_reviewed',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(seller_profile.user.get_full_name(), seller_profile.user.email)],
                context = {
                    'review': review
                }
            )

def decline_buyer_purchase_hndlr(sender, **kwargs):
    ''''notify the buyer that the seller has declined his purchase request'''
    if sender == ItemForSale:
        item = kwargs['instance']
        seller_profile = item.owner.get_profile()
        buyer_profile = kwargs['buyer'].get_profile()
        message = kwargs['message']
        new_note = Notification(post_from=item, going_to=buyer_profile, type=11)
        new_note.second_party = seller_profile
        thread = Thread.objects.get(owner=buyer_profile.user, post_id=item.id, other_person=seller_profile.user)
        new_note.thread_id = thread.id
        new_note.save()
        buyer_profile.friend_notifications += 1
        buyer_profile.save()
        buyer_full_name = buyer_profile.user.get_full_name()

        if buyer_profile.message_email:
            send_email_task.delay(
                template_name='decline_buyer',
                from_email='BuyNearMe <noreply@buynear.me>',
                recipient_list=[add_name_to_email(buyer_full_name, buyer_profile.user.email)],
                context={
                    'message':message.body,
                    'post':item.id,
                    'sender':seller_profile.user.get_full_name(),
                    'recipient':buyer_full_name,
                    'thread':thread.id
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
confirm_purchase_signal.connect(confirm_purchase_hndlr, sender=ItemForSale, dispatch_uid="confirmed")
decline_seller_purchase_signal.connect(decline_seller_purchase_hndlr, sender=ItemForSale, dispatch_uid="declined_seller")
decline_buyer_purchase_signal.connect(decline_seller_purchase_hndlr, sender=ItemForSale, dispatch_uid="declined_buyer")
item_reviewed_signal.connect(item_reviewed_handler, sender=ItemReview, dispatch_uid="item_reviewed")
