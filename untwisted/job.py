from threading import *
from untwisted.mode import Mode
from untwisted import core
from untwisted.core import get_event

DONE = get_event()
class Job(Thread, Mode):
    def __init__(self, func, *args, **kwargs):
        Thread.__init__(self)
        Mode.__init__(self)

        self.func   = func
        self.args   = args
        self.kwargs = kwargs
        self.data   = None
        core.gear.pool.append(self)
        self.start()
    
    def run(self):
        self.data = self.func(*self.args, **self.kwargs)
        core.gear.wake()

    def update(self):
        self.drive(DONE, self.data)



