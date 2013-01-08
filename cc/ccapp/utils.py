from ccapp.models import *
from templated_email import send_templated_mail

def send_bnm_message(request):
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
            from_email='Buy Near Me <noreply@buynear.me>',
            recipient_list=[recipient.email],
            context={
                'message':message.body,
                'thread':thread2,
                'post':post,
                'username':sender.username,
                'first_name':sender.first_name,
                'full_name':sender.get_full_name(),
                'recipient_name':recipient_name,
                },
        )