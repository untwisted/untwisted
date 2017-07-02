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
            dispatcher.add_map(ind, self.unpin, events)

    def unpin(self, dispatcher, *args):
        for ind in args[-1]:
            dispatcher.del_map(ind, self.unpin, args[-1])
        self.count = self.count - 1

    def update(self):
        if self.count: return
        self.drive(DONE)
        core.gear.pool.remove(self)
        



