from traceback import print_exc as debug
from mode import *


xmap  = lambda obj, *args: obj.bind(*args)
zmap  = lambda obj, *args: obj.unbind(*args)
spawn = lambda obj, *args: obj.drive(*args)

def cmap(mode, event, handle, *args):
    """

    """

    def cave(*event_args):
        zmap(mode, event, cave, *args)
        seq = handle(*event_args)
        # It cant be unlinked here because
        # if it happens an exception on handle
        # it wouldnt be unlinked and it would
        # keep trying to call handle.
        # zmap(mode, event, cave, *args)
        return seq
    
    xmap(mode, event, cave, *args)

def die():
    """
    It is used to stop the reactor.
    """
    raise Kill





