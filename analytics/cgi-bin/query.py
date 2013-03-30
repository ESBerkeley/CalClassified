#!/usr/bin/python

import os
import SetQuery
import json
import urllib

from operator import *


import datetime

import base64


'''


example usage: 

http://localhost:8000/cgi-bin/query.py?.filter("TIME.the_time",gt,datetime.datetime.now()-datetime.timedelta(minutes=30))

that shows all data where the time of the entry is newer than 30 minutes ago


'''

'''
os.system('sleep 1')
os.system('beep')
os.system('sleep 1')'''

def insert(doc, tag_string, instr):
    return doc[1:doc.find(tag_string)] + instr + doc[doc.rfind(tag_string)+len(tag_string):]



sq = SetQuery.SetQuery()

#Load the html template to trick the cgi server
f = open('template/fakedash.html','r')
thedoc = f.read()



#x = urllib.unquote(os.environ.get('QUERY_STRING'))

x = base64.b64decode(os.environ.get('QUERY_STRING'))

#x = urllib.unquote(".all().filter(%27TIME.the_time%27,%20gt,%20%272013/03/26%2000:00:00%27).filter(%27TIME.the_time%27,%20lt,%20%272013/03/30%2000:00:00%27)")


exec("sq.all()" + x)


thedoc = insert(thedoc, "~!@$%^&*()_+", "#J.S.O.N#" + json.dumps(sq.data) + "#J.S.O.N#")

print thedoc



