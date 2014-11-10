from untwisted.network import Spin, xmap, READ, spawn
from socket import socket, AF_INET, SOCK_STREAM, error
from threading import *
from errno import EWOULDBLOCK, EAGAIN

CODE = (EWOULDBLOCK, EAGAIN)

class Machine(Thread):
    def __init__(self, job, func, *args, **kwargs):
        Thread.__init__(self)

        self.job    = job
        self.func   = func
        self.args   = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        data = self.func(*self.args, **self.kwargs)
        #self.job.queue.append((self.getName(), data))
        
        # I thought using this to avoid the threads
        # having to send bytes whenever they have done
        # the task but it seems it wouldnt work cause
        # self.job.queue.append would block until
        # self.dispatch going over all the items
        # and spawning the events.

        #state = self.job.lock.locked()

        #if not state:
        #    self.job.active()
        
        self.job.active(self.getName(), data)

class Job(Spin):
    def __init__(self):
        # I have to improve this code.
        # i have to handle the exception
        # if the port is in use etc. 
     
        Spin.__init__(self)
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        self.connect_ex(server.getsockname())

        sock, addr = server.accept()
        self.sock  = sock
        server.close()

        xmap(self, READ, self.dispatch)
        
        self.lock  = Lock()
        self.ident = None
        self.data  = None

    def register(self, callback, *args, **kwargs):
        thread = Machine(self, callback, *args, **kwargs)
        return thread.getName()
    
    @staticmethod
    def dispatch(self):
        try:
            self.recv(1)
        except error, (err, msg):
            if err in CODE:
                return
            else:
                raise

        spawn(self, self.ident, self.data)
        self.lock.release()


    def active(self, ident, data):
        """
        This function is supposed to be called by threads.
        It attempts to wake up the reactor by sending
        a byte to the socket spin instance.

        It tries continously send the byte it fails
        if a call self.sock.send throws an exception
        whose error code isn't in CODE.

        It sends the bytes even if the reactor isn't blocked.

        It has to be so otherwise we get into an unecessary complexity.
        """
        self.lock.acquire()

        self.ident = ident
        self.data  = data

        while True:
            try:
                self.sock.send(' ')
                break
            except error, (err, msg):
                if not err in CODE:
                    self.lock.release()
                    raise

job = Job()

