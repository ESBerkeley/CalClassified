'''
Scrape our information from google analytics, and paste the most useful bits into html.
This is not a true substitute for the full GA package, just a quick tie in for basic stuff.

'''

from monitor import Monitor
#import utils.gdata.src.gdata.analytics.client
#import utils.gdata.src.gdata.analytics.sample_util


class google_ga(Monitor):
    
    name = "google_ga"
    htmltag = '%GA%'

    #This should obtain relevant data, and return a dict
    def scrapeData(self):
        '''
        email="red3king@gmail.com"  # Set these values
        password="7v9c7w788jeczztop$"
        table_ids = (
            'ga:TABLE_ID',          # TABLE_ID for first website
            'ga:TABLE_ID',          # TABLE_ID for second website
                                    # (...)
        )

        SOURCE_APP_NAME = 'UA-34571639-1'
        client = gdata.analytics.client.AnalyticsClient(source=SOURCE_APP_NAME)
        client.client_login(email, password, source=SOURCE_APP_NAME, service=client.auth_service)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        print "Visitors yesterday"
        for table_id in table_ids:   
            data_query = gdata.analytics.client.DataFeedQuery({
                'ids': table_id,
                'start-date': yesterday.isoformat(),
                'end-date': yesterday.isoformat(),
                'dimensions': 'ga:date',
                'metrics': 'ga:visitors'})

        feed = client.GetDataFeed(data_query)
        print "%s : %s" % (feed.data_source[0].table_name.text, feed.entry[0].metric[0].value)
        '''

        return {'whee':23}

    #This is passed a list of the dicts returned by scrapedata. The latest is last.
    #A list of dicts is returned as opposed to just the latest in order to show graphs over time.
    def render(self, inputarr):
        html = ''
        html += '12123 unique page views <br>'
        html += "<a href='http://www.ga.com'>Full Google Analytics Page</a>"
        return html



