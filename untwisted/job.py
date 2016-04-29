from threading import Thread, Lock
from untwisted import core
from untwisted.waker import waker
from untwisted.event import DONE, ERROR
from untwisted.dispatcher import Dispatcher

class Job(Thread, Dispatcher):
    """
    This class is used to execute a function inside a thread.

        def func(a, b):
            return a + b
    
        def on_done(job, sum):
            print sum
    
        job = Job(func, 1, 2)
        xmap(job, DONE, on_done)
    
    In case of an exception occuring inside func then the event 
    ERROR happens instead of the DONE event which carries the exception thrown.    
    """

    def __init__(self, func, *args, **kwargs):
        Thread.__init__(self)
        Dispatcher.__init__(self)
        self.func         = func
        self.args         = args
        self.kwargs       = kwargs
        self.data         = None
        self.is_done      = False
        self.err          = None
        self.lock         = Lock()

        core.gear.pool.append(self)
        self.start()

    def run(self):
        try:
            self.data = self.func(*self.args)
        except Exception as err:
            with self.lock:
                self.err = True
        else:
            with self.lock:
                self.is_done = True
        finally:
            waker.wake_up()

    def update(self):
        with self.lock:
            if self.is_done:
                self.process()
        
    def process(self):
        if self.err:
            self.drive(ERROR, self.err)
        else:
            self.drive(DONE, self.data)
        core.gear.pool.remove(self)




