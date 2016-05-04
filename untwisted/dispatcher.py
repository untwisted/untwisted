from traceback import print_exc as debug
from untwisted.core import Kill, Root
import inspect

class Stop(Exception):
    """
    This exception is used to avoid remaining handles being
    processed for a given event.

    from untwisted.dispatcher import Dispatcher, Stop
    
    def handle0(dispatcher):
        raise Stop
    
    def handle1(dispatcher):
        print 'it will not be processed!'
    
    dispatcher = Dispatcher()
    dispatcher.add_map('alpha', handle0)
    dispatcher.add_map('alpha', handle1)
    dispatcher.drive('alpha')
    """
    pass

class Erase(Exception):
    """
    When this exception is thrown from a handle it avoids such a handle
    being processed again upon its event.

    from untwisted.dispatcher import Dispatcher, Erase
    
    def handle(dispatcher):
        print 'It will be called just once!'
        raise Erase
    
    dispatcher = Dispatcher()
    dispatcher.add_map('alpha', handle)
    dispatcher.drive('alpha')
    dispatcher.drive('alpha')
    """

    pass

class Dispatcher(object):
    """
    The event dispatcher class.
    """

    base = dict()
    def __init__(self):
        self.base = dict()
        self.pool = list()

    def drive(self, event, *args):
        """
        Used to dispatch events.
        """

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
        """
        Add a mapping like event -(arg0, arg1, arg2, ...)-> handle.
        """

        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def del_map(self, event, handle, *args):
        """
        Remove a mapping like event -(arg0, arg1, arg2, ...)-> handle.
        """
        if args:
            self.base[event].remove((handle, args))
        else:
            self.base[event] = filter(lambda ind: 
                        ind[0] != handle, self.base[event])

    def install_maps(self, *args):
        """
        Install a set of mappings.
        """

        for ind in args:
            self.add_map(*ind)

    def insert_map(self, index, map):
        """

        """

        pass

    process_static_base = classmethod(process_base)
    add_static_map      = classmethod(add_map)
    del_static_map      = classmethod(del_map)

    def add_handle(self, handle):
        """
        Whenever an event occurs then handle is processed.
        """

        self.pool.append(handle)

    def del_handle(self, handle):
        """
        Avoid handle from being processed when a given event occurs.
        """

        self.pool.remove(handle)

xmap  = lambda dispatcher, *args: dispatcher.add_map(*args)
zmap  = lambda dispatcher, *args: dispatcher.del_map(*args)
spawn = lambda dispatcher, *args: dispatcher.drive(*args)

def once(dispatcher, event, handle, *args):
    """
    Used to do a mapping like event -> handle
    but handle is called just once upon event.
    """

    def shell(dispatcher, *args):
        try:
            handle(dispatcher, *args)
        except Exception as e:
            raise e
        finally:
            dispatcher.del_map(event, shell)
    dispatcher.add_map(event, shell, *args)








