from time import time
from UserDict import UserDict
from untwisted.network import spawn, imap, smap
from untwisted.mode import *
import core

slc      = lambda x: x[0]
minimal  = lambda x, y: x if x < y and x != core.gear.default_timeout else y
COMPLETE = core.get_event()

class Task(Mode):
    """
    This class abstracts the concept of *finished task*. 
    
    As untwisted is purely based on events we will want to know when a given set of
    events were spawned and under which conditions them were spawned.

    In order to keep track of some events this class implements methods
    that will help us deal with it.

    """

    def __init__(self, data):
        Mode.__init__(self)
        self.data  = data
        self.count = 0

    def gather(self, con, *jobs):
        """
        This function is used to spread conditions that must be
        satisfied. When all the conditions are satisfied Task instance
        will spawn an event COMPLETE. 

        """

        # We use it to self removing handles.
        base = list()

        for event, cond  in jobs:
            ident = smap(con, event, self.cave, base, event, cond)
            base.append(ident) 
        
        # The self.count represents the number
        # of tasks which weren't executed yet.
        self.count = self.count + 1


    def cave(self, args, base, event, cond):
        """
        This function shouldn't be called outside untwisted.
        """

        val = cond(self.data, event, args)

        if not val: 
            return

        for ind in base: 
            ind()

        self.count = self.count - 1

        if not self.count: 
            spawn(self, COMPLETE, self.data)




class Schedule(object):
    """ Used to have callbacks called in a given period of time """
    def __init__(self):
        core.gear.pool.append(self)
        self.base = dict()

    def after(self, inc, cbck, opt, *args):
        """ 
        Executes a callback after inc.
        If opt is set as True then it executes
        just once.
        """

        self.base[inc, cbck] = [time(), args, opt]
        core.gear.timeout    = minimal(core.gear.timeout, inc)

    def unmark(self, inc, cbck):
        """ 
        Unmark a callback 
        """

        del self.base[inc, cbck]

        data              = map(slc, self.base.keys())
        value             = reduce(minimal, data, core.gear.default_timeout)
        core.gear.timeout = value


    def update(self):
        for inc, cbck in self.base.keys():
            init, args, opt = self.base[inc, cbck]
            
        # It checks whether the difference
        # between the initial time and the final
        # time against the increment.
        # Note: the correct order is.
        # self.base[inc, cbck][0] = time()
        # cbck(*args)
        # because if sched.unmark is called from cbck
        # it will throw an exception due to the key not existing
        # anymore
            if time() - init >= inc: 
                self.base[inc, cbck][0] = time()
                cbck(*args)
        # If opt flag is set as True
        # we don't want to execute it
        # anymore.
                if opt: self.unmark(inc, cbck)


#################
sched = Schedule()

__all__ = ['sched', 'Schedule']


