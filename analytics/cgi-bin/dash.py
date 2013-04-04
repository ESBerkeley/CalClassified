#!/usr/bin/python

from utils.misc import is_live
from utils.hardwarestats import hardwareStats
from utils.time import timeMonitor
from utils.BNM_hooks import bnm_hooks
from utils.GA import google_ga
from utils.bnm_log_reader import bnm_log_reader

from datetime import date, datetime
import json


hwmon = hardwareStats()
time = timeMonitor()
ga = google_ga()
bnm = bnm_hooks()
blm = bnm_log_reader()


monitors = [hwmon, time, ga, bnm, blm]



def insert(doc, tag_string, instr):
    return doc[0:doc.find(tag_string)] + instr + doc[doc.rfind(tag_string)+len(tag_string):]


now = date.today()

if is_live():
    filename = "/var/www/calclassified/logs/"

else:
    filename = "../../logs/"

filename += str(now.year) + "_" + str(now.month) + "_" + str(now.day) + ".json"   

todayslog = open(filename, "r")
todayslog.seek(0)
log_data = json.loads(todayslog.read())




if len(log_data) > 0:
    most_recent_data = log_data[len(log_data)-1]

else:
    most_recent_data = {}


#Load the html template, asshole
f = open('template/dash.html','r')
thedoc = f.read()


#Call each monitor's render, and insert results into template.

field_selector_list = []

for mon in monitors:

    #Here, we construct a list consisting of all of this monitor's earlier reports.    

    try:
        monitor_data = [x[mon.name] for x in log_data]

    except KeyError:
        monitor_data = {}

    if thedoc.find(mon.htmltag) >= 0:
        thedoc = insert(thedoc, mon.htmltag, mon.render(monitor_data))

    for field in mon.fields:
        field_selector_list.append({'name': mon.name + ':' + field['name'], 'type': field['type']})



thedoc = insert(thedoc, '%^@_@^%', 'var field_selector_list = ' + json.dumps(field_selector_list))

print thedoc
