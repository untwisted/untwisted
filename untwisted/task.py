from untwisted.dispatcher import Dispatcher
from untwisted.event import DONE
from untwisted import core

class Task(Dispatcher):
    """
    """

    def __init__(self):
        Dispatcher.__init__(self)
        self.count = 0

    def start(self):
        core.gear.pool.append(self)

    def add(self, dispatcher, *events):
        """
        """
        self.count = self.count + 1
        for ind in events:
            dispatcher.add_map(ind, self.exced, events)

    def exced(self, dispatcher, *args):
        for ind in args[-1]:
            dispatcher.del_map(ind, self.exced, args[-1])
        self.count = self.count - 1

    def update(self):
        if self.count <= 0: 
            self.destroy() 

    def destroy(self):
        self.drive(DONE)
        core.gear.pool.remove(self)
        



