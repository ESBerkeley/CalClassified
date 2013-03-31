import logging
import datetime


#This decotrator will log what users access a wrapped view, along with the time of access.
def logit(fn):

    def asd(*fish):
        #starfish[0] is request, other arguments are accepted to pass to the view.

        swamp_logger = logging.getLogger('swamp_logger')
        fname = fn.__name__
        user = ''

        if fish[0].user.is_authenticated():
            user = str(fish[0].user.id)
        else:
            user = '-1'

        fmt_string = '%Y/%m/%d %H:%M:%S'

        timestr = datetime.datetime.now().strftime(fmt_string)

        swamp_logger.info('logit_analytics: user ' + user + ' view ' + fname + ' time [' + timestr + ']')  

        return fn(*fish)

    return asd


#Call this when more must be logged than a simple time of access. (for that, use easier logit decorator)
def custom_log_message(message):
    swamp_logger = logging.getLogger('swamp_logger')
    fmt_string = '%Y/%m/%d %H:%M:%S'
    timestr = datetime.datetime.now().strftime(fmt_string)
    swamp_logger.info('custom_analytics: ' + message + ' time [' + timestr + ']')


