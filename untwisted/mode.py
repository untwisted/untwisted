from traceback import print_exc as debug

class Mode(object):
    def __init__(self):
        self.base = dict()

    def drive(self, event, *args):
        """ Spreads an event """
        try:
            item = self.base[event]
        except KeyError:
            pass
        else:
            for handle, data in item[:]:
                try:
        # We call the handle associated to event.
        # if it returns an iterator we just chain it.
                    seq = handle(self, *(args + data))
        # In case of not having an iterator we go on 
        # processing.
                    if not seq:
                        continue
        # It chains the iterator.
                    point = next(seq)
                    point(self, seq)
        # It stops processing handles linked to event.
                except Stop:
                    break
        # It stops all the sequence of events.
                except Kill, Root:
                    raise
                except StopIteration:
                    pass
        # It prints the exception. 
                except Exception:
                    debug()

    def link(self, event, handle, *args):
        """ Used to link a handle to an event """

        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def unlink(self, event, handle, *args):
        """ Use args to unmap the handle """

        # It shouldnt have printed exceptions if the event 
        # doesnt exist since a call to spin.destroy()
        # would clear all the events and some handles
        # would try to unlinke themselves from the spin
        # it wouldnt be like a real problem.
        try:
            self.base[event].remove((handle, args))
        except KeyError:
            pass



class Stop(Exception):
    pass

class Root(Exception):
    pass

class Kill(Exception):
    pass



