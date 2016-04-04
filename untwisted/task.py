from untwisted.dispatcher import Dispatcher
from untwisted.event import DONE

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
            dispatcher.add_map(ind, self.is_done, events)

    def is_done(self, dispatcher, *args):
        self.count = self.count - 1

        for ind in args[-1]:
            dispatcher.del_map(ind, self.is_done, args[-1])

        if not self.count: 
            self.drive(DONE)




