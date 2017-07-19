from __future__ import print_function
from builtins import str
from traceback import print_exc 
import pprint

def on_all(*args):
    pprint.pprint(args)

def on_event(con, *args):
    pprint.pprint(args)

def debug(event, params):
    print('Event:%s' % event)
    print('Args:%s' % str(params))
    print_exc()




