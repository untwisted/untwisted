from untwisted.event import READ, WRITE, CLOSE, DESTROY
from select import *
from socket import *

class Root(Exception):
    pass

class Kill(Exception):
    pass

def die(msg=''):
    """
    It is used to stop the reactor.
    """

    print(msg)
    raise Kill

class Gear:
    """ 
    It implements a basic set of methods that should be
    common to all reactors.

    """

    MAX_SIZE = 6028
    def __init__(self):
        self.pool = []

    def mainloop(self):
        """ 
        This is the reactor mainloop.
        """
            
        while True:
            try:
                self.update()
            except Kill:
                break
            except KeyboardInterrupt:
                print(self.base)
                raise

    def process_pool(self):
        """ 
        Process a pool of objects that 
        should be updated when the reactor is not idling.
        """
        for ind in self.pool[:]:
            ind.update()

    def update(self):
        """
        This method is intented to be subclassed by
        reactor classes.
        """

    def register(self, ssock):
        pass

    def unregister(self, ssock):
        pass

        pass


class Select(Gear):
    """
    This reactor is select based. It is default on non posix platforms.
    """

    def __init__(self):
        self.timeout = None
        self.default_timeout = None

        self.base  = []

        # These are the sockets in R/W status.
        self.rsock = set()
        self.wsock = set()
        Gear.__init__(self)

    def update(self):
        """ 
        """

        self.process_pool()
        self.process_reactor()

    def process_reactor(self):
        """
        """

        for ind in self.base: 
            self.scale(ind)

        rsock, wsock, xsock = select(self.rsock, 
            self.wsock, self.base, self.timeout)

        for ind in rsock:
            try:
                ind.drive(READ)
            except Root:
                pass

        for ind in wsock:
            try:
                ind.drive(WRITE)
            except Root:
                pass

        for ind in xsock:
            try:
                ind.drive(CLOSE)
            except Root:
                pass

    def register(self, ssock):
        """
        """

        self.base.append(ssock)

    def unregister(self, ssock):
        """
        """

        self.base.remove(ssock)

        self.rsock.discard(ssock)
        self.wsock.discard(ssock)
        ssock.drive(DESTROY)

    def scale(self, ssock):
        """
        """

        if ssock.base.get(READ):
            self.rsock.add(ssock)
        else:
            self.rsock.discard(ssock)

        if ssock.base.get(WRITE):
            self.wsock.add(ssock)
        else:
            self.wsock.discard(ssock)

class Epoll(Gear):
    """
    This reactor is epoll based. It is default on posix platforms.
    """

    def __init__(self):
        Gear.__init__(self)
        # epoll uses -1 as default for timeout.
        self.timeout         = -1
        self.default_timeout = -1
        self.base            = dict()
        self.pollster        = epoll()


    def update(self):
        """
        """

        self.process_pool()
        self.process_reactor()

    def process_reactor(self):
        """
        """

        for ind in self.base.values():
            self.scale(ind)

        events = self.pollster.poll(self.timeout) 
        for fd, event in events:
            self.dispatch(fd, event)

    def register(self, ssock):
        """
        """

        self.base[ssock.fd] = ssock
        self.pollster.register(ssock.fd)

    def unregister(self, ssock):
        """
        """

        # Note: 
        # ssock0 = SuperSocket()
        # fd0   = ssock0.fileno()
        # ssock0.destroy()
        # ssock0.close()
        # ssock1 = SuperSocket()
        # fd1   = ssock1.fileno()
        # fd1 == fd0 -> True

        del self.base[ssock.fd]
        self.pollster.unregister(ssock.fd)
        ssock.drive(DESTROY)

    def scale(self, ssock):
        """
        """

        # Note: In case of registering for
        # EPOLLERR	Error condition happened on the assoc. fd
        # When a connection is tried and it is refused
        # it would spawn twice CONNECT_ERR.
        is_readable = EPOLLIN  if ssock.base.get(READ) else 0 
        is_writable = EPOLLOUT if ssock.base.get(WRITE) else 0
        mask        = is_readable | is_writable
        self.pollster.modify(ssock.fd, mask)

    def dispatch(self, fd, event):
        """
        """

        ssock = self.base[fd]

        if event & EPOLLIN:
            try:
                ssock.drive(READ)
            except Root:
                pass

        if event & EPOLLOUT:
            try:
                ssock.drive(WRITE)
            except Root:
                pass

class Poll:
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.base    = []
       
def install_reactor(reactor, *args, **kwargs):
    global gear
    gear = reactor(*args, **kwargs)
    #print 'Using %s reactor' % reactor

def default():
    try:
        install_reactor(Epoll)
    except NameError:
        install_reactor(Select)

default()
# install_reactor(Select)
# install_reactor(Epoll)


