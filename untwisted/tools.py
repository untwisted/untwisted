from untwisted.dispatcher import Erase

class Hold(object):
    def __init__(self, seq):
        self.seq                    = seq
        self.dispatcher, self.event = next(seq)
        self.dispatcher.add_map(self.event, self)

    def __call__(self, dispatcher, *args):
        try:
            dispacher, event = self.seq.send(args)
        except StopIteration:
            self.dispatcher.del_map(self.event, self)
        else:
            if self.dispatcher != dispatcher or event != self.event:
                self.swap_dispatcher(event, dispatcher)

    def swap_dispatcher(self, event, dispatcher):
        self.dispatcher.del_map(self.event, self.dispatcher)
        dispatcher.add_map(event, self)
        self.dispatcher  = dispatcher
        self.event       = event

def coroutine(handle):
    def start(*args, **kwargs):
        hold = Hold(handle(*args, **kwargs))
    return start

def mapcall(handle):
    """
    """

    def shell(dispatcher, *args):
        dispatcher.drive(handle, handle(dispatcher, *args))
    return shell

def handle_exception(*ex):
    """
    """

    def wrapper(handle):
        def shell(dispatcher, *args):
            try:
                value = handle(dispatcher, *args)
            except ex as e:
                dispatcher.drive((handle, e.__class__), e)
        return shell
    return wrapper

def mapclass(handle):
    """
    """

    def shell(self, dispatcher, *args):
        dispatcher.drive(self, handle(dispatcher, *args))
    return shell

def class_exception(*ex):
    """
    """

    def wrapper(handle):
        def shell(self, dispatcher, *args):
            try:
                value = handle(self, dispatcher, *args)
            except ex as e:
                dispatcher.drive((self, e.__class__), e)
        return shell
    return wrapper



