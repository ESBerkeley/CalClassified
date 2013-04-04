'''
   This monitor reads the logs generated by the swamp_logger in the buynearme code, and parses it to a format readable by the analytics package.

'''
import datetime
from misc import is_live

class bnm_log_reader():

    name = "bnm_log_reader"
    htmltag = '%BLR%'

    if is_live():
        logfile = "/var/www/calclassified/logs/"
    else:
        logfile = "../../logs/"
    
    logfile += 'bnm_log.log'

    fields = [
        {'name': 'buybutton_clicks', 'type': 'number'},
        {'name': 'sale_completeds', 'type': 'number'},
        {'name': 'item_reposts', 'type': 'number'},
        {'name': 'messages_sent', 'type': 'number'},
    ]
 

    def scrapeData(self):
        buybutton_clicks = 0
        sale_completeds = 0
        item_reposts = 0
        messages_sent = 0

        try:
            f = open(self.logfile,'r')
            alllines = f.readlines()

            for line in alllines:

                if self.found(line, 'time'):
                    if datetime.datetime.now() - self.gettime(line) <= datetime.timedelta(minutes = 3000):
                        if self.found(line, 'logit_analytics'):
                            #If a line starts with "logit_analytics", then it has been generated by the @logit decorator
                            #applied to a view.
                            if self.found(line, 'view sendmessage'):
                                messages_sent += 1
    
                        elif self.found(line, 'custom_analytics'):
                            #If a line starts with "custom_analytics", then it has been generated by a manual call to 
                            #custon_log_message()
                            if self.found(line, 'bought item'):
                                buybutton_clicks += 1
                            elif self.found(line, 'reposted_item'):
                                item_reposts += 1
                            elif self.found(line, 'sold item'):
                                sale_completeds += 1                     

        except KeyError:
            buybutton_clicks = -1
            sale_completeds = -1
            item_reposts = -1
            messages_sent = -1

        out_dict = {}
        out_dict['buybutton_clicks'] = buybutton_clicks
        out_dict['sale_completeds'] = sale_completeds
        out_dict['item_reposts'] = item_reposts
        out_dict['messages_sent'] = messages_sent

        return out_dict


    def render(self, inputarr):
        return 'bnm_log_reader has no implemented latest-data renderer yet'



    def gettime(self, strin):

        timestr = strin[strin.index('[')+1:strin.index(']')]
        return datetime.datetime.strptime(timestr,"%Y/%m/%d %H:%M:%S")


    #Get around silly python exception crap 
    #ok dammit now I learn about a find function that dosen't throw exceptions
    #Well, I already wrote this, so whatever.
    def found(self, strin, substr):
        try:
            strin.index(substr)
            return True
        except:
            return False

