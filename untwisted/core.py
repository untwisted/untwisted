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

        pass


class Select(Gear):
    """
    This reactor is select based. It is default on non posix platforms.
    Althought one could specifically use this reactor in posix platforms.
   

    from untwisted.network import *
    install_reactor(core.Select)

    def hello_world():
        print 'hello world'

    from untwisted.task import *
    sched.after(3, hello_world, True)
    core.gear.mainloop()


    If it isn't intented to use the default reactor
    the new reactor must be replaced after importing
    untwisted.network objects and before any other
    import.
    """

    def __init__(self):
        """
        This constructor initializes basic structures
        that compose the reactor public and internal interface.
        """

        # This variable holds the timeout passed
        # to select.
        self.timeout = None

        # This is the default timeout. It is used
        # by objects being processed in pool.
        self.default_timeout = None

        # These are the sockets in R/W status.
        self.rsock = []
        self.wsock = []
        self.xsock = []
        Gear.__init__(self)


    def update(self):
        """ 
        This method polls the sockets using select. 
        It spawns either READ or WRITE.

        If one intents to use this reactor with some other
        reactor it might be called from other mainloop.
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
        if spin.base.get(READ) and not spin in self.rsock:
            self.rsock.append(spin)

        if spin.base.get(WRITE) and not spin in self.wsock:
            self.wsock.append(spin)

    def unregister(self, spin):
        if not spin.base.get(READ):
            try:
                self.wsock.remove(spin)
            except ValueError:
                pass

        if not spin.base.get(WRITE):
            try:
                self.wsock.remove(spin)
            except ValueError:
                pass


class Epoll(Gear):
    """
    This reactor is epoll based. It is default on posix platforms.


    from untwisted.network import *
    core.gear.mainloop()
    print core.gear 

    
    It will print the Epoll class instance if you are on a posix platform.
    When we import a module that requires access to the reactor instance
    the default reactor is automatically installed.


    from untwisted.task import *
    # It prints...
    # Using <class 'untwisted.core.Epoll'> reactor
    """

    def __init__(self):
        """ It defines basic structures. """

        # epoll uses -1 as default for timeout.
        self.timeout         = -1
        self.default_timeout = -1

        # It maps file descriptors to their Spin instances.
        self.atom  = dict()
        self.epoll = epoll()
        Gear.__init__(self)


    def update(self):
        """
        This method polls sockets with epoll. 
        It spawns either READ or WRITE.

        If one intents to use this reactor with some other
        reactor it might be called from other mainloop.

        """
        self.process_pool()
        
        # We need first scale which sockets have handles
        # linked to READ or WRITE events.
        # So, we filter those handles and modify their
        # spin's file descriptors to wait for the exact
        # set of events with self.epoll.poll method.
        # I could avoid to scale the sockets using this 
        # approach if i implemented a system of callbacks
        # in the Mode class. The methods link, unlink would
        # receive two callbacks. One would be called whenever
        # one adds a event, and the other one would be called
        # whenever one unlinks a event from a callback.
        # So, when one links READ to a handle it would have
        # callback that automatically modifies its file descriptor
        # mask in the self.epoll instance same thing would occur
        # with one linking WRITE to a handle, it would automatically
        # modify the flag. So we wouldnt need to filter all the sockets
        # to change their flags. I am not sure if it is worth
        # since i would considerably add a bit more of complexity
        # and it could affect the performance from other parts of
        # the program using untwisted.
        self.scale()

        # The epoll.poll method returns a list of (fd, event)
        # pairs.
        self.resource = self.epoll.poll(self.timeout) 
        
        # Once we have that list we can process.
        self.process_atom()

    def scale(self, spin):
        """
        It scales sockets for writting/reading events.

        It shouldn't be called outside untwisted library.
        """

        # It goes through self.atom scalling the 
        # spin instances that have READ/WRITE
        # handles installed.
        for fd, spin in self.atom.iteritems():
            item = spin.base.get(READ)

        # If the spin instance has a handle
        # installed on READ then we should inform
        # self.epoll to look for readiness status.
            mask_x = EPOLLIN if item else 0 

            item = spin.base.get(WRITE)
        # The logic works for WRITE.
            mask_y = EPOLLOUT if item else 0
        
        # We finally modify the file descriptor flag.
            self.epoll.modify(fd, mask_x | mask_y)

    def process_atom(self):
        """
        This function shouldn't be called outside untwisted.

        It goes through self.resource driving the proper
        events.
        """

        for fd, event in self.resource:
        # It might be the case that the
        # actual spin instance corresponding
        # to the fd was removed from the atom.
        # it is one called its destroy method.
        # So, we check for it.
        # The idea is making it possible to destroy
        # Spin instances from handles being called from
        # anywhere of the program.
            spin = self.atom.get(fd)
            
            if spin:
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
        """
        This function registers a spin/socket instance
        to be used with epoll reactor. 
        
        It shouldn't be called outside untwisted.
        """

        # We will futurely use fd to unregister
        # the socket. Since fileno() is a unix thing
        # i dont think it is good idea to save fd
        # in spin from Spin.__init__ constructor.
        # If i called spin.fileno from unregister
        # and the socket had been closed it would
        # throw an exception.
        spin.fd            = spin.fileno()
        self.atom[spin.fd] = spin
        self.epoll.register(spin.fd)


    def unregister(self, spin):
        """
        This function unregisters a spin/socket from
        the epoll reactor.

        It shouldn't be called outside untwisted.
        """

        del self.atom[spin.fd]
        self.epoll.unregister(spin.fd)

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


