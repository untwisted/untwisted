from traceback import print_exc 
import pprint

def debug(event, params):
    print 'Event:%s' % event
    print 'Args:%s' % str(params)
    print_exc()



