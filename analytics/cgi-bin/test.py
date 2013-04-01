import SetQuery
from operator import *

x = SetQuery.SetQuery()

print x.filter("TIME.the_time",eq,"02:39:58").data

