from ccapp.views import *
#from templated_email import send_templated_mail

def send_bnm_message(request):
    body = request.POST['message']
    recipient_pk = request.POST['recipient_pk']
    post_pk = request.POST['post_pk']
    post = ItemForSale.objects.get(id=int(post_pk))
    sender = request.user
    recipient = User.objects.get(id=int(recipient_pk))
    print(recipient)
    if post.pending_flag:
        if request.user not in [post.owner, post.pending_buyer]:
            
            return HttpResponse("crap " + request.user.username + post.owner.username + post.pending_buyer.username) #crap someone else got it before you, sorrym8

    else:
        post.pending_buyer = request.user
        post.pending_flag = True
        post.save()
    
    
    message = Message()
    message.body = body
    message.post_title = post.title
    message.sender = sender
    message.recipient = recipient
    message.save()

    first_message = False        

    #Create 2 Threads for both ends
    try: #see if thread exists, if not create it
        thread1 = Thread.objects.get(owner=sender, other_person=recipient, post_title=post.title, post_id=post.id)
    except:
        thread1 = Thread.objects.create(owner=sender, other_person=recipient, post_title=post.title, post_id=post.id)
        first_message = True
    try: #see if thread exists, if not create it
        thread2 = Thread.objects.get(owner=recipient,other_person=sender, post_title=post.title, post_id=post.id)
    except:
        thread2 = Thread.objects.create(owner=recipient,other_person=sender, post_title=post.title, post_id=post.id)

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