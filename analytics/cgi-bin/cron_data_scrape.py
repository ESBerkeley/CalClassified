
from utils.hardwarestats import hardwareStats
from utils.time import timeMonitor
from utils.BNM_hooks import bnm_hooks
from utils.GA import google_ga



from datetime import date, datetime
import json

now = date.today()

filename = str(now.year) + "_" + str(now.month) + "_" + str(now.day) + ".json"


todayslog = open(filename, "a+")
todayslog.seek(0)
logdata = todayslog.read()
todayslog.close()

todayslog = open(filename, "w")



old_data = []

try:
    old_data = json.loads(logdata)

except:
    old_data = []


hwmon = hardwareStats()
time = timeMonitor()
ga = google_ga()
bnm = bnm_hooks()

monitors = [hwmon,time,ga,bnm]
new_stats = {}

for mon in monitors:
    new_stats[mon.name] = mon.scrapeData()



old_data = old_data + [new_stats]

todayslog.write(json.dumps(old_data))

todayslog.close()


