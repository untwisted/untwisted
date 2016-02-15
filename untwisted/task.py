from untwisted.dispatcher import Dispatcher
from untwisted.event import COMPLETE

class Task(Dispatcher):
    """
    """

    def __init__(self):
        Mode.__init__(self)
        self.count = 0

    def add(self, dispatcher, *jobs):
        """
        """

        self.count = self.count + 1


    def cave(self, args, base, event, cond):
        """
        """




