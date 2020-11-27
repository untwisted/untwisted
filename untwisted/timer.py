from untwisted import core
import bisect
import time

class CancelCall(Exception):
    pass

class Timer:
    base = []
    def __init__(self, interval, callback, *args, **kwargs):
        self.args = args
        self.interval = interval
        self.time = time.time()
        self.callback = callback
        self.kwargs = kwargs

        core.gear.pool.append(self)
        bisect.insort(Timer.base, interval)
        self.set_reactor_timeout()

    def update(self):
        if time.time() - self.time > self.interval:
            self.exec_callback()

    def exec_callback(self):
        self.callback(*self.args, **self.kwargs)
        self.cancel()

    def cancel(self):
        core.gear.pool.remove(self)
        Timer.base.remove(self.interval)
        self.set_reactor_timeout()

    def set_reactor_timeout(self):
        core.gear.timeout = Timer.base[0] if Timer.base else core.gear.default_timeout


class Sched(Timer):
    def update(self):
        if time.time() - self.time > self.interval:
            self.exec_callback()

    def exec_callback(self):
        try:
            self.callback(*self.args, **self.kwargs)
        except CancelCall:
            self.cancel()
        else:
            self.time = time.time()
    

