'''
  Think of this as a queryset on log data, for making analytics queries easily.
  Filtering queries may be chained.

'''

from os import listdir
import json

from utils.misc import is_live
from utils.hardwarestats import hardwareStats
from utils.time import timeMonitor
from utils.BNM_hooks import bnm_hooks
from utils.GA import google_ga

from datetime import date, datetime



class SetQuery:


    def __init__(self):
        self.data = None

        hwmon = hardwareStats()
        time = timeMonitor()
        ga = google_ga()
        bnm = bnm_hooks()

        self.monitors = [hwmon, time, ga, bnm]



    def all(self): #Load data from all json files found
        self.data = []

        if is_live():
            dir = "/var/www/calclassified/logs/"
        else:
            dir = "../logs/"

        for jsonfile in listdir(dir):

            if len(jsonfile.split(".")) > 1:

                if jsonfile.split(".")[1] == "json":
                    fd = open(dir + jsonfile, "r")
                    snippet = json.loads(fd.read())

                    for hourly_chunk in snippet:
                        self.data.append(hourly_chunk)

        return self


    #Example use of filter to find when there are more than nine new pms:
    #from operator import *
    #SetQuery.filter("bnm_hooks.bnm_dict.new_pms", ge, 10)
 
    def filter(self, fieldName, operation, value):

        if self.data is None:
            self.all()
            
        newdata = []

        relevantMonitor = None
        

        monitorName = fieldName.split('.')[0]
        morselpath = fieldName.split('.')[1:]
        concat_morselpath = ""

        for x in morselpath:
            concat_morselpath += x + '___'


        for monitor in self.monitors:
            if monitor.name == monitorName:
                
                relevantMonitor = monitor


                #If the operation is a string, it must be the name of a custom monitor comparison method. 
                if type(operation) == 'str':
                    if hasattr(monitor, concat_morselpath + operation):
                        operation = getattr(monitor, operation)
                    else:
                        pass ######## uh oh

                #If the operator exists, check if there is a monitor specific override:
                else:
                    if hasattr(monitor, concat_morselpath + operation.__name__):
                        
                        operation = getattr(monitor, concat_morselpath +  operation.__name__)
                    else:
                        
                        pass


        for reading in self.data:
            morsel = reading
            for subdict_name in fieldName.split('.'):
                morsel = morsel[subdict_name]

            if operation(morsel,value):
                newdata.append(reading)


        self.data = newdata

        return self
