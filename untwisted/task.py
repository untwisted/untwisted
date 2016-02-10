from time import time
from UserDict import UserDict
from untwisted.network import spawn, imap, smap
from untwisted.mode import *
from untwisted import core
from untwisted.event import COMPLETE

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


