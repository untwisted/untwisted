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
        self.base = dict()
        self.pool = list()

    def drive(self, event, *args):
        try:
            self.process_base(event, args)
        except KeyError:
            pass

        try:
            self.process_static_base(event, args)
        except KeyError:
            pass

        for handle in self.pool:
            handle(self, event, args)

    def process_base(self, event, args):
        for handle, data in self.base[event][:]:
            try:
                seq = handle(self, *(args + data))
            except Stop:
                break
            except StopIteration:
                pass
            except Kill, Root:
                raise
            except Erase:
                self.base[event].remove((handle, data))
            except Exception as e:
                debug()
                self.drive(Exception, handle, e)

    def add_map(self, event, handle, *args):
        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def del_map(self, event, handle, *args):
        if args:
            self.base[event].remove((handle, args))
        else:
            self.base[event] = filter(lambda ind: 
                        ind[0] != handle, self.base[event])

    def install_maps(self, *args):
        for ind in args:
            self.add_map(*ind)

    def insert_map(self, index, map):
        pass

    process_static_base = classmethod(process_base)
    add_static_map      = classmethod(add_map)
    del_static_map      = classmethod(del_map)

    def add_handle(self, handle):
        self.pool.append(handle)

    def del_handle(self, handle):
        self.pool.remove(handle)

xmap  = lambda dispatcher, *args: dispatcher.add_map(*args)
zmap  = lambda dispatcher, *args: dispatcher.del_map(*args)
spawn = lambda dispatcher, *args: dispatcher.drive(*args)




