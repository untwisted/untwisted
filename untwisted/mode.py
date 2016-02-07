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

    def process_iters(self, chain, args):
        for seq in chain[:]:
            try:
                del self.iters_base[event]
                event = next(seq)
                self.iters_base[event] = seq
                seq.send(args)
            except Stop:
                break
            except Kill, Root:
                raise
            except StopIteration:
                pass
            except Exception:
                debug()

    def bind(self, event, handle, *args):
        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def unbind(self, event, handle, *args):
        self.base[event].remove((handle, args))



