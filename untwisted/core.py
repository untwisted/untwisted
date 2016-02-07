"""
"""

from select import *
from socket import *
from untwisted.mode import *

# Whenever we use get_event it increases
# So we don't get events messed.
event_count = 0

def get_event():
    """ 
    It returns a new event signal.

    from untwisted.network import *
    X = get_event()
    Y = get_event()
    print X
    print Y


    Whenever we call get_event it increases the integer
    corresponding to the signal. That avoids events getting
    messed through modules.
    """

    global event_count

    event_count = event_count + 1
    return event_count

# When a socket is ready for reading 
# the chosen reactor will spawn READ.
READ  = get_event()

# When a socket is ready for writting
# it will spawn WRITE.
WRITE = get_event()

class Gear(object):
    """ 
    It implements a basic set of methods that should be
    common to all reactors.

    This class isn't intented to be subclassed outside untwisted
    modules.

    I thought of installing the reactor inside this class
    instead of inside this module. However, it arose some
    odd patterns which i preferred to avoid. 

    """

    MAX_SIZE = 6028
    def __init__(self):
        """ Class constructor """
        self.pool = []

    def mainloop(self):
        """ 
        This is the reactor mainloop.
        It is intented to be called when
        a reactor is installed.

        from untwisted.network import *

        # It processes forever.
        core.gear.mainloop()
        """
            
        while True:
        # It calls repeteadly the reactor
        # update method.
            try:
                self.update()
            except Kill:
        # It breaks the loop
        # silently.
        # people implementing reactors from other mainloop
        # should implement this try: catch
        # suitably to their needs.

                break

    def process_pool(self):
        """ 
        This method processes the pool of objects
        that are binded to the reactor. 

        This method shouldn't be called by the
        user of the class except he knows what he is
        doing.
        """
        for ind in self.pool:
            ind.update()

    def update(self):
        """
        This method is intented to be subclassed by
        reactor classes.
        """

    def add(self, spin):
        pass

    def remove(self, spin):
        pass

        pass


class Select(Gear):
    """
    This reactor is select based. It is default on non posix platforms.
    """

    def __init__(self):
        # This variable holds the timeout passed
        # to select.
        self.timeout = None

        # This is the default timeout. It is used
        # by objects being processed in pool.
        self.default_timeout = None

        self.base  = []

        # These are the sockets in R/W status.
        self.rsock = set()
        self.wsock = set()
        self.xsock = set()
        Gear.__init__(self)

    def update(self):
        """ 
        Other reactors should call this method.
        """

        self.process_pool()
        rsock, wsock, xsock = select(self.rsock , self.wsock , self.xsock, self.timeout)

        # This has to be in this order.
        # If a socket is in the list of WRITE event
        # it is expecting either to write or if it has connected.
        # If process_rsock is called first and the socket has connected
        # and the client has sent bytes you will not have your handle_connect
        # called first.

        for ind in wsock:
            try:
                ind.drive(WRITE)
            except Root:
                pass

        for ind in rsock:
            try:
                ind.drive(READ)
            except Root:
                pass

    def register(self, spin):
        self.base.append(spin)

    def unregister(self, spin):
        self.base.remove(spin)

    def scale(self, spin):
        try:
            self.update_wsock(spin)
        except KeyError:
            pass

        try:
            self.update_rsock(spin)
        except KeyError:
            pass

    def update_rsock(self, spin):
        if spin.is_readable():
            self.rsock.add(spin)
        else:
            self.rsock.remove(spin)

    def update_wsock(self, spin):
        if spin.is_writable():
            self.wsock.add(spin)
        else:
            self.wsock.remove(spin)


class Epoll(Gear):
    """
    This reactor is epoll based. It is default on posix platforms.
    """

    def __init__(self):
        # epoll uses -1 as default for timeout.
        self.timeout         = -1
        self.default_timeout = -1

        # It maps file descriptors to their Spin instances.
        self.base  = dict()
        self.epoll = epoll()
        Gear.__init__(self)


    def update(self):
        """
        Other reactors should call this method.
        """

        self.process_pool()

        # The epoll.poll method returns a list of (fd, event)
        # pairs.
        resource = self.epoll.poll(self.timeout) 

        for fd, event in resource:
            try:
                spin = self.base[fd]
            except KeyError:
                pass
            else:
                if event & EPOLLOUT:
                    try:
                        spin.drive(WRITE)
                    except Root:
                        pass
     
                if event & EPOLLIN:
                    try:
                        spin.drive(READ)
                    except Root:
                        pass

    def register(self, spin):
        self.base[fd] = spin
        self.epoll.register(fd)

    def unregister(self, spin):
        del self.base[spin.fd]
        self.epoll.unregister(spin.fd)

    def scale(self, spin):
        r  = EPOLLIN if spin.is_readable() else 0 
        w  = EPOLLOUT if spin.is_writable() else 0
        fd = spin.fileno()

        self.epoll.modify(fd, r | w)


class Poll(object):
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.atom    = []
       

def install_reactor(reactor, *args, **kwargs):
    global gear
    gear = reactor(*args, **kwargs)
    #print 'Using %s reactor' % reactor

def default():
    try:
        install_reactor(Epoll)
    except NameError:
        install_reactor(Select)

# default()
install_reactor(Select)

__all__ = ['get_event', 'READ', 'WRITE' , 'install_reactor']



