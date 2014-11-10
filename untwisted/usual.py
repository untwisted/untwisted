from traceback import print_exc as debug
from mode import *


xmap  = lambda obj, *args: obj.link(*args)
zmap  = lambda obj, *args: obj.unlink(*args)
spawn = lambda obj, *args: obj.drive(*args)

def rmap(mode, event, handle):
    """

    """

    c     = 0
    scope = mode.base[event]

    while True:
        try:
            if scope[c][0] == handle:
                del scope[c]
            else:
                c = c + 1
        except IndexError:
            break

def nmap(mode, event, handle, count, *args):
    """

    """

    c = 0
    def cave(*event_args):
        if c >= count:
            zmap(mode, event, cave, *args)
        else:
            seq = handle(*event_args)
            c   = c + 1
            return seq

    xmap(mode, event, cave, *args)

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

def mmap(mode, event_list, handle, *extra):
    """

    """

    def cave(*args):
        ret = handle(*(args + extra))

        for ind in event_list:
            zmap(mode, ind, cave, *args)
        return ret

    for ind in event_list:
        xmap(mode, ind, cave, *extra)

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

def setup(mode, shell, *args, **kwargs):
    """ This function is just a different way of doing
        Protocol(spin, *args, **kwargs).
        It sounds more consistent.
        Obs: Classes that wrap spin objects
        can be seen as a 'shell'.

        I could store a list of installed protocols
        in the mode class so whenever one wants to
        advantage the set of protocols installed in a class
        he would call switch. It would match the idea
        that some protocols should be persistent and
        advantaged in new connection instances. we
        would lose the callbacks installed in raw
        with xmap, but those callbacks are meant
        to be connection dependent somehow.
        or i could just do

        protocols = [Protocol_1, Protocol_2, Protocol_3]
        then for ind in protocols:
                ind(do stuff)


    """
    shell(mode, *args, **kwargs)
   
def bind(mode, shell, *args, **kwargs):
    """

    """

    shell.__init__(mode, *args, **kwargs)

def hook(mode_x, mode_y, *args):
    """

    """

    for ind in args:
        smap(mode_y, ind, 
             lambda event_args, event=ind: mode_x.drive(event, *event_args))

def switch(mode_x, mode_y):
    """ This function switchs spin_y context
        to spin_x context. 
    """
    pass


def die():
    """
    It is used to stop the reactor.
    """
    raise Kill





