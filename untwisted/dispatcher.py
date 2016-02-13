from traceback import print_exc as debug
from untwisted.core import Kill, Root
import inspect

class Stop(Exception):
    pass

class Erase(Exception):
    pass

class Dispatcher(object):
    base = dict()
    def __init__(self):
        self.base  = dict()
        self.pool = dict()

    def drive(self, event, *args):
        try:
            self.process_base(self.base, event, args)
        except KeyError:
            pass

        try:
            self.process_base(Dispatcher.base, event, args)
        except KeyError:
            pass

        for handle in self.pool:
            handle(self, event, args)

    def process_base(self, base, event, args):
        for handle, data in base[event]:
            try:
                seq = handle(self, *(data + args))
            except Stop:
                break
            except StopIteration:
                pass
            except Kill, Root:
                raise
            except Erase:
                base[event].remove(handle, handle)
            except Exception as e:
                debug()
                self.drive(e.__class__, e)
    
    def add_map(self, event, handle, *args):
        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def del_map(self, event, handle, *args):
        self.base[event].remove((handle, args))

    @classmethod
    def add_static_map(event, handle, *args):
        item = Dispatcher.base.setdefault(event, list())
        item.append((handle, args))

    @classmethod
    def del_static_map(event, handle, *args):
        pass

    def add_handle(self, handle):
        pass

    def del_handle(self, handle):
        pass

def coroutine(handle):
    def start_iter(*args, **kwargs):
        seq = handle(*args, **kwargs)
        mode, event = next(seq)

        def exec_iter(m, e, a):
            if e != event: 
                return

            seq.send(a)
            m, e = next(seq)

            if e != event:
                event = e

            if m == mode: 
                return

            mode.del_handle(exec_iter)
            m.add_handle(exec_iter)
            mode = m
        mode.add_handle(exec_iter)
    return start_iter




