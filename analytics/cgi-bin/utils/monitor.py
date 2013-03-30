'''
This is a superclass for monitors.

'''

class Monitor():

    name = "rather_useless"
    htmltag = '%0%'

    #fields is a list of all fields which may be displayed on the dashboard
    fields = []
    #example : fields = [{'name' : 'cpu_load', 'type' : 'int'}, {'name' : 'newest_member', 'type' : 'str'}] 
    #The name of a field is expected to be the key for the data in a monitor's dict. (sub-dict keys are concatenated, seperated by spaces)


    #This should obtain relevant data, and return a dict
    def scrapeData(self):
        return {}

    #This is passed a list of the dicts returned by scrapedata. The latest is last.
    #A list of dicts is returned as opposed to just the latest in order to show graphs over time.
    def render(self, inputarr):
        return ''




