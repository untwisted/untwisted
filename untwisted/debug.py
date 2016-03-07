import pprint

def on_all(*args):
    pprint.pprint(args)

def on_event(con, *args):
    pprint.pprint(args)



