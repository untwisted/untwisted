from traceback import print_exc as debug
import inspect

class Stop(Exception):
    pass

class Root(Exception):
    pass

class Kill(Exception):
    pass


class Mode(object):
    # I MUST IMPLEMENT A 
    # xmap(spin, ALL, handle)
    # that works with iters.
    base = dict()
    def __init__(self):
        self.base  = dict()
        self.iters = dict()

    def drive(self, event, *args):
        try:
            chain = self.base[event]
        except KeyError:
            pass
        else:
            self.process_handles(event, chain, args)

        try:
            chain = self.iters[event]
        except KeyError:
            pass
        else:
            self.process_iters(chain, args)


    def process_handles(self, event, chain, args):
        for handle, data in chain[:]:
            try:
                seq = handle(self, *(args + data))
            except Stop:
                break
            except Kill, Root:
                raise
            except Exception:
                debug()

    def process_iters(self, event, chain, args):
        for seq in chain[:]:
            try:
                mode, e = next(seq)
            except Stop:
                break
            except Kill, Root:
                raise
            except StopIteration:
                self.iters_base[event].remove(seq)
            except Exception:
                debug()
            else:
                if e != event or not mode is self:
                    self.iters_base[event].remove(seq)
                if e != event:
                    mode.iters_base[event].add(seq)
                seq.send(args)

    def bind(self, event, handle, *args):
        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def unbind(self, event, handle, *args):
        self.base[event].remove((handle, args))

    @classmethod
    def bind_static(event, handle, *args):
        pass

    @classmethod
    def bind_iter(seq):
        pass

