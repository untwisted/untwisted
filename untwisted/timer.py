from untwisted import core
import bisect
import time

class CancelCall(Exception):
    pass

class Timer(object):
    base = []
    def __init__(self, inc, callback, *args, **kwargs):
        self.args         = args
        self.kwargs       = kwargs
        self.inc          = inc
        self.time         = time.time()
        self.callback     = callback
        core.gear.pool.append(self)
        bisect.insort(Timer.base, inc)
        self.set_reactor_timeout()

    def update(self):
        if not time.time() - self.time > self.inc:
            return
        self.callback(*self.args, **self.kwargs)
        self.cancel()

    def cancel(self):
        core.gear.pool.remove(self)
        Timer.base.remove(self.inc)
        self.set_reactor_timeout()

    def set_reactor_timeout(self):
        core.gear.timeout = Timer.base[0] if Timer.base else core.gear.default_timeout


class Sched(Timer):
    def update(self):
        if not time.time() - self.time > self.inc:
            return

        try:
            self.callback(*self.args, **self.kwargs)
        except CancelCall:
            self.cancel()
        else:
            self.time = time.time()



