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

class HandleProcessor(object):
    def __call__(self, handle):
        self.handle = handle
        return self.process_handle

    def __init__(self, *excpts):
        self.excpts = excpts

class handle_exception(HandleProcessor):
    def process_handle(self, dispatcher, *args):
        try:
            value = self.handle(dispatcher, *args)
        except self.excpts as e:
            dispatcher.drive((self.process_handle, e.__class__), e)

class mapcall(HandleProcessor):
    def process_handle(self, dispatcher, *args):
        try:
            value = self.handle(dispatcher, *args)
        except self.excpts as e:
            dispatcher.drive((self.process_handle, e.__class__), e)
        else:
            dispatcher.drive(self.process_handle, value)

def coroutine(handle):
    def start(*args, **kwargs):
        hold = Hold(handle(*args, **kwargs))
    return start


