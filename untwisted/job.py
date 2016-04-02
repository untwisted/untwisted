from threading import Thread, Lock
from untwisted import core
from untwisted.waker import waker

class Job(Thread):
    def __init__(self, handle, func, *args, **kwargs):
        Thread.__init__(self)

        self.func    = func
        self.args    = args
        self.kwargs  = kwargs
        self.data    = None
        self.is_done = False
        self.handle  = handle
        core.gear.pool.append(self)
        self.lock       = Lock()

        self.start()
    
    def run(self):
        self.data = self.func(*self.args, **self.kwargs)

        with self.lock:
            self.is_done = True
        waker.wake_up()

    def update(self):
        with self.lock:
            if self.is_done: 
                self.drive()

    def drive(self):
        self.handle(self.data)
        core.gear.pool.remove(self)








