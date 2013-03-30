from monitor import Monitor

from os import system
from commands import getoutput


class hardwareStats(Monitor):

    name = "Hardware Statistics"
    htmltag = '%1%'
    critical_services = ['rabbitmq-server', 'apache2', 'celeryd', 'sshd']

    fields = [
      {'name': 'loadinfo.one', 'type': 'number'},
      {'name': 'loadinfo.five', 'type': 'number'},
      {'name': 'loadinfo.fifteen', 'type': 'number'}
    ]


    def check_service(self,sname):
        down = True

        for k in getoutput('ps aux | grep ' + sname).split('\n'):
            if -1 == k.find('grep'):
                down = False

        return down



    def scrapeData(self):
        hwdict = {}

        #Get memory usage information from /proc/meminfo (simply cut the first five lines)
        f = open('/proc/meminfo','r')

        meminfo = ''
        for k in range(5):
            meminfo += f.readline() + '<br>'

        hwdict['meminfo'] = meminfo



        #Add on load information from /proc/loadavg
        f = open('/proc/loadavg')
        
        loadinfo = f.readline()
        loadinfo = loadinfo.split(' ')
        loadinfo2 = {'one':loadinfo[0], 'five':loadinfo[1], 'fifteen':loadinfo[2]}
        
        hwdict['loadinfo'] = loadinfo2

        #Find and report whether ps can see our critical services.        
        hwdict['services'] = {}
        for service in self.critical_services:
            hwdict['services'][service] = self.check_service(service)   

        return hwdict



    def render(self, hwlist):

        if len(hwlist) > 0:
            hwdict = hwlist[len(hwlist)-1]
        else:
            hwdict = {}

        html = ''

        #Show memory usage information
        html += '<h4>Memory</h4>'
        meminfo = hwdict.get('meminfo')

        if meminfo:
            html += meminfo
        else:
            html += 'Memory usage information unavailable'


        #Display load information
        html += '<h4>System Load</h4>'
        loadinfo = hwdict.get('loadinfo')
        if loadinfo:
            html += 'One minute load avg:  ' + loadinfo['one'] + '<br>'
            html += 'Five minute load avg: ' + loadinfo['five'] + '<br>'
            html += 'Fifteen minute load avg: ' + loadinfo['fifteen'] + '<br>'
        else:
            html += 'Memory Information unavailable in records'


        #Displays whether critical things are still alive
        html += '<h4>Critical Tasks</h4>'
    
        services = hwdict.get('services')

        if services:
            for sname in self.critical_services:
                try:
                    if services[sname]:
                        html += "<b>CRITICAL: " + sname + "<font color='red'> <blink>DOWN</blink></font></b> <br>"
                    else:
                        html += sname + " <font color='green'> <b>UP</b> </font>"
                except:
                    html += sname + " : data unavailable"

        return html





