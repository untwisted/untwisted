from traceback import print_exc as debug
from untwisted.dispatcher import Kill

xmap  = lambda obj, *args: obj.add_map(*args)
zmap  = lambda obj, *args: obj.del_map(*args)
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

def imap(mode, event, handle, *args):
    """

    """

    xmap(mode, event, handle, *args)

    def cave():
        zmap(mode, event, handle, *args)
    return cave

def smap(mode, event, handle, *extra):
    """

    """

    def cave(*args):
        handle(args, *extra)

    ident = imap(mode, event, cave)
    return ident

def die():
    """
    It is used to stop the reactor.
    """
    raise Kill




