
from celery.task import Task
from celery.registry import tasks

from ccapp.models import *
from django_facebook.models import *

from templated_email import send_templated_mail


class send_email_task(Task):
    def run(self, template_name, from_email, recipient_list, context, **kwargs):
        try:

            #our email templates use model instances, but passing them through signals is bad.
            #So, ids are passed in and the instances are looked up here.

            if 'post' in context: 
                context['post'] = ItemForSale.objects.get(pk=context['post'])

            if 'thread' in context:
                context['thread'] = Thread.objects.get(pk=context['thread'])            

            send_templated_mail(
                template_name=template_name,
                from_email=from_email,
                recipient_list=recipient_list,
                context=context,
            )

        except:
            pass




tasks.register(send_email_task)




#class send_email_task():
#def send_email_task_delay(template_name, from_email, recipient_list, context, **kwargs):
#         
#            context['post'] = ItemForSale.objects.get(pk = context['post'])
#            context['thread'] = Thread.objects.get(pk = context['thread'])
#           
#            send_templated_mail(
#                template_name=template_name,
#                from_email=from_email,
#                recipient_list=recipient_list,
#                context=context,
#            )




