'''
This scrapes custom data from bnm app.

'''

import sys
from monitor import Monitor
from django.core.management import setup_environ

class bnm_hooks(Monitor):

    name = "bnm_hooks"
    htmltag = '%BNM%'
    fields = [
      {'name': 'new_ifs', 'type': 'number'}, 
      {'name': 'new_pms', 'type': 'number'}, 
      {'name': 'new_comments', 'type': 'number'}, 
      {'name': 'new_notifs', 'type': 'number'}, 

      {'name': 'total_ifs', 'type': 'number'}, 
      {'name': 'total_pms', 'type': 'number'}, 
      {'name': 'total_comments', 'type': 'number'}, 
      {'name': 'total_notifs', 'type': 'number'}, 
      
      {'name': 'browse_hits', 'type': 'number'},
      {'name': 'new_users', 'type': 'number'},
      {'name': 'total_users','type':'number'}
    ]

    #This should obtain relevant data, and return a dict
    def scrapeData(self):
        loadfail = False
        #Load up into django.
        #This path must obviously be changed.
        try:
            sys.path.append('/home/rory/cc/CalClassified/cc')
            import settings
            setup_environ(settings)
            from ccapp.models import ItemForSale
            from django_facebook.models import *
            import datetime
        except:
            loadfail = True

        bnm_dict = {}

        if not loadfail:

            bnm_dict['new_ifs'] = len(ItemForSale.objects.filter(time_created__gte = datetime.datetime.now() - datetime.timedelta(minutes = 30)))  
            bnm_dict['new_pms'] = len(Message.objects.filter(time_created__gte = datetime.datetime.now() - datetime.timedelta(minutes = 30)))  
            bnm_dict['new_comments'] = len(Comment.objects.filter(time_created__gte = datetime.datetime.now() - datetime.timedelta(minutes = 30)))  
            bnm_dict['new_notifs'] = len(Notification.objects.filter(time_created__gte = datetime.datetime.now() - datetime.timedelta(minutes = 30)))  
            bnm_dict['new_users'] = len(User.objects.filter(date_joined__gte = datetime.datetime.now() - datetime.timedelta(minutes = 30)))  

        
            bnm_dict['total_ifs'] = len(ItemForSale.objects.all())
            bnm_dict['total_pms'] = len(Message.objects.all())
            bnm_dict['total_comments'] = len(Comment.objects.all())
            bnm_dict['total_notifs'] = len(Notification.objects.all())
            bnm_dict['total_user'] = len(User.objects.all())


        browsehits = -1
 
        try:
            browsehits = 0

            f = open('/var/log/apache2/access.log')
            lines = f.readlines()
            l2 = []
            for line in lines:
                try:
                    line.index('GET /browse/ ')
                    l2.append(line)
                except:
                    pass

            for line in l2:
                timefield = line.split(' ')[3][1:]
                access_date = datetime.datetime.strptime(timefield,"%d/%b/%Y:%H:%M:%S")
                if (datetime.datetime.now() - access_date < datetime.timedelta(minutes = 30)):
                    browsehits += 1
                
        except:
            browsehits = -1

        bnm_dict['browse_hits'] = browsehits

        return bnm_dict



    def render(self, inputarr):
        html = ''

#        import json
#        return json.dumps(inputarr)


        try:
            latest_bnm_stats = inputarr[len(inputarr)-1]
            lbs = latest_bnm_stats
            html += '<div class = "row">'
            html += '<div class = "span2">'
            html += '<h4>New (Last 30 minutes)</h4>'
            html += str(lbs['new_ifs']) + ' new Items For Sale <br>'
            html += str(lbs['new_pms']) + ' new Personal Messages <br>'
            html += str(lbs['new_comments']) + ' new comments <br>'
            html += str(lbs['new_notifs']) + ' new notifications issued <br>'
            html += str(lbs['new_users']) + 'new users <br>'
            html += '</div>'

            html += '<div class = "span2">'
            html += '<h4>Totals</h4>'
            html += str(lbs['total_ifs']) + ' Items for Sale <br>'
            html += str(lbs['total_pms']) + ' Personal Messages<br>'
            html += str(lbs['total_comments']) + ' Comments <br>'
            html += str(lbs['total_notifs']) + ' Notifications <br>'
            html += str(lbs['total_users']) + ' Users <br>'
            html += '</div>'
            html += '</div>'

        except: 
            latest_bnm_stats = {}
            html = 'No BNM data available.'
    
        return html
        




