from threading import Thread, Lock
from untwisted.mode import Mode
from untwisted import core
from untwisted.core import get_event
from untwisted.waker import waker

DONE = get_event()
class Job(Thread, Mode):
    def __init__(self, func, *args, **kwargs):
        Thread.__init__(self)
        Mode.__init__(self)

        self.func    = func
        self.args    = args
        self.kwargs  = kwargs
        self.data    = None
        self.is_done = False
        core.gear.pool.append(self)
        self.start()
    
    def run(self):
        self.data = self.func(*self.args, **self.kwargs)

        # it has to be set here otherwise we get in trouble
        # because the reactor will call update that will access self.is_done.
        self.is_done = True
        waker.wake_up()

    def update(self):
        if not self.is_done: return
        self.drive(DONE, self.data)
        core.gear.pool.remove(self)





