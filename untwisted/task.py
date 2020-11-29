from untwisted.dispatcher import Dispatcher
from untwisted.event import DONE
from untwisted import core

class Task(Dispatcher):
    """
    Used to keep track of events. It spawns DONE when all
    events that were specified happen with a given set of Dispatcher instances.
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
            dispatcher.add_map(ind, self.check_tasks, events)

    def check_tasks(self, dispatcher, *args):
        self.count = self.count - 1
        for ind in args[-1]:
            dispatcher.del_map(ind, self.check_tasks, args[-1])

    def update(self):
        if self.count <= 0: 
            self.destroy() 

    def destroy(self):
        self.drive(DONE)
        core.gear.pool.remove(self)
        



