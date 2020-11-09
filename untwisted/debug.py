from builtins import str
from traceback import print_exc 
from untwisted.event import CODE
import pprint

def on_all(*args):
    pprint.pprint(args)

def on_event(con, *args):
    pprint.pprint(args)

def debug(event, params):
    print('Event:%s' % CODE[event])
    print('Args:%s' % str(params))
    print_exc()





