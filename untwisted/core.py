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
            except KeyboardInterrupt:
                print(self.base)
                raise

    def process_pool(self):
        """ 
        This method processes the pool of objects
        that are binded to the reactor. 

        This method shouldn't be called by the
        user of the class except he knows what he is
        doing.
        """
        for ind in self.pool[:]:
            ind.update()

    def update(self):
        """
        This method is intented to be subclassed by
        reactor classes.
        """

    def register(self, spin):
        pass

    def unregister(self, spin):
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
        self.process_reactor()

    def process_reactor(self):
        """
        """

        for ind in self.base: 
            self.scale(ind)

        rsock, wsock, xsock = select(self.rsock , 
        self.wsock, self.base, self.timeout)

        for ind in rsock:
            try:
                ind.drive(READ)
            except Root:
                pass

        wsock = (ind for ind in wsock if not ind.dead)
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

    def register(self, spin):
        """
        """

        self.base.append(spin)

    def unregister(self, spin):
        """
        """

        self.base.remove(spin)

        self.rsock.discard(spin)
        self.wsock.discard(spin)
        spin.drive(DESTROY)

    def scale(self, spin):
        """
        """

        if spin.base.get(READ):
            self.rsock.add(spin)
        else:
            self.rsock.discard(spin)

        if spin.base.get(WRITE):
            self.wsock.add(spin)
        else:
            self.wsock.discard(spin)

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
        Other reactors should call this method.
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

    def register(self, spin):
        """
        """

        self.base[spin.fd] = spin
        self.pollster.register(spin.fd)

    def unregister(self, spin):
        """
        """

        # Note: 
        # spin0 = Spin()
        # fd0   = spin0.fileno()
        # spin0.destroy()
        # spin0.close()
        # spin1 = Spin()
        # fd1   = spin1.fileno()
        # fd1 == fd0 -> True

        del self.base[spin.fd]
        self.pollster.unregister(spin.fd)
        spin.drive(DESTROY)

    def scale(self, spin):
        """
        """

        # Note: In case of registering for
        # EPOLLERR	Error condition happened on the assoc. fd
        # When a connection is tried and it is refused
        # it would spawn twice CONNECT_ERR.
        is_readable = EPOLLIN  if spin.base.get(READ) else 0 
        is_writable = EPOLLOUT if spin.base.get(WRITE) else 0
        mask        = is_readable | is_writable
        self.pollster.modify(spin.fd, mask)

    def dispatch(self, fd, event):
        """
        """

        spin = self.base[fd]

        if event & EPOLLIN:
            try:
                spin.drive(READ)
            except Root:
                pass

        if event & EPOLLOUT and not spin.dead:
            try:
                spin.drive(WRITE)
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

# default()
install_reactor(Select)
# install_reactor(Epoll)


