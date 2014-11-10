from usual import xmap, zmap

class hold(object):
    """ This class is used to wait events from a given Mode class.
    """
    def __init__(self, target, *event_list):
        # Where we wait the event from.
        self.target     = target
        self.event_list = event_list

    def __call__(self, mod, seq):
        # Where it is being processed.
        self.mod = mod
        self.seq = seq
        
        # It links all events to self.chain when
        # one of them is issued self.chain is called.
        for ind in self.event_list:
            xmap(self.target, ind, self.chain, ind)

        # It is used to stop the chain of events.
        raise StopIteration

    def chain(self, *args):
        try:
        # We will need to know which event was fired.
        # So, we just make the event be the first argument
        # returned by hold.
            temp = (args[-1], args[:-1])
        # Send it inside the iterator.
            point = self.seq.send(temp)
        # It checkes if we are still on the prvious event.
        # If it isn't it chains the new event.
            if not point is self:
                point(self.mod, self.seq)
        except Exception as excpt:
        # If something goes wrong it just removes all handles.
            for ind in self.event_list:
                zmap(self.target, ind, self.chain, ind)
        # It raises up the exception to debug.
            raise excpt


