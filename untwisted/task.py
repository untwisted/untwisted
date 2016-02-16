from untwisted.dispatcher import Dispatcher
from untwisted.event import COMPLETE

class Task(Dispatcher):
    """
    """

    def __init__(self):
        Dispatcher.__init__(self)
        self.count = 0

    def add(self, dispatcher, *events):
        """
        """

        self.count = self.count + 1

        for ind in events:
            dispatcher.add_map(ind, self.checker, events)

    def checker(self, dispatcher, events):
        """
        """
        self.count = self.count - 1

        for ind in events:
            dispatcher.del_map(ind, self.checker)

        if self.count:
            self.drive(COMPLETE)



