import datetime

'''
    A simple monitor which returns/renders the time.

'''


class timeMonitor():

    name = "TIME"
    htmltag = '%TIME%'
    fields = [] #Time is special, for now

    fmt_string = '%Y/%m/%d %H:%M:%S'

    def scrapeData(self):
        return {'the_time': datetime.datetime.now().strftime(self.fmt_string)}

    
    def render(self, inputarr):
        try:
            latest = inputarr[len(inputarr)-1]
        except:
            latest = {}

        timestr = ''
 
        try:
            timestr = latest['the_time']
        except:
            timestr = 'Time is not in record.'
        
        return timestr




    def the_time___eq(self,t1,t2):
        try:
            t1 = datetime.datetime.strptime(t1,self.fmt_string)
            if type(t2) == type('asdf'):
              t2 = datetime.datetime.strptime(t2,self.fmt_string)
       
            return t1 == t2

        except:
            return False


    def the_time___lt(self,t1,t2):
        try:
            t1 = datetime.datetime.strptime(t1,self.fmt_string)
            if type(t2) == type('asdf'):
              t2 = datetime.datetime.strptime(t2,self.fmt_string)
            return t1 < t2
        except:
            return False


    def the_time___gt(self,t1,t2):
        try:
            t1 = datetime.datetime.strptime(t1,self.fmt_string)
            if type(t2) == type('asdf'):
              t2 = datetime.datetime.strptime(t2,self.fmt_string)
            return t1 > t2
        except:
            return False


    def the_time___lte(self,t1,t2):
        try:
            t1 = datetime.datetime.strptime(t1,self.fmt_string)
            if type(t2) == type('asdf'):
              t2 = datetime.datetime.strptime(t2,self.fmt_string)
            return t1 <= t2
        except:
            return False


    def the_time___gte(self,t1,t2):
        try:
            t1 = datetime.datetime.strptime(t1,self.fmt_string)
            if type(t2) == type('asdf'):
              t2 = datetime.datetime.strptime(t2,self.fmt_string)
            return t1 >= t2
        except:
            return False
