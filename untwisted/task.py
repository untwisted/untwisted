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
            dispatcher.once(ind, self.check_tasks)

    def check_tasks(self, dispatcher, *args):
        self.count = self.count - 1

    def update(self):
        if self.count <= 0: 
            self.destroy() 

    def destroy(self):
        self.drive(DONE)
        core.gear.pool.remove(self)
        



