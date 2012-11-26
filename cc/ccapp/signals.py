
from django_facebook.signals import user_registered
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch.dispatcher import Signal

from ccapp.models import ItemForSale, Notification
from django_facebook.models import FacebookUser, FacebookProfile



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
                new_note = Notification(post_from = post, going_to = dude)
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


