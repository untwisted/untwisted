from untwisted.core import Kill, Root
from traceback import print_exc

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

def debug(event, params):
    print('Event:%s' % repr(event))
    print('Args:%s' % str(params))
    print_exc()

class Dispatcher:
    """
    The event dispatcher class.
    """

    def __init__(self):
        self.base = dict()

    def drive(self, event, *args):
        """
        Used to dispatch events.
        """

        maps = self.base.get(event)
        if not maps:
            return False

        for handle, data in maps[:]:
            params = args + data
            try:
                handle(self, *params)
            except Stop:
                break
            except StopIteration:
                pass
            except (Kill, Root) as e:
                raise
            except Erase:
                maps.remove((handle, data))
            except Exception as e:
                debug(event, params)
        return True

    def update_base(self, base):
        """
        Extend a Dispatcher instance base with other Dispatcher instance events.
        
        Example:

        disp0 = Dispatcher()
        disp1 = Dispatcher()
        disp0.update_base(disp1.base)
        """

        for ind in base.items():
            maps = self.base.setdefault(ind[0], [])
            maps.extend(ind[1])

    def del_map(self, event, handle, *args):
        """
        Used to unbind a handle for a given event.

        The *args parameter has to be the same objects that
        were used to bind the handle.
        """

        self.base[event].remove((handle, args))

    def del_all(self, event, handle):
        """
        Remove all handles for a given event.
        """

        maps  = self.base[event]
        for ind in maps[:]:
            if ind[0] is handle:
                maps.remove(ind)

    def once(self, event, handle, *args):
        """
        Execute a handle just once.
        """
    
        def handle_wrapper(dispatcher, *args):
            self.del_map(event, handle_wrapper, *args)
            handle(dispatcher, *args)
        self.add_map(event, handle_wrapper, *args)
        return handle_wrapper

    def install_maps(self, *args):
        """
        A shorthand to bind multiple handles at once.

        The *args parameter is a sequence of tuples like.

        ((event0, handle, args), ...)
        """

        for ind in args:
            self.add_map(*ind)

    def add_map(self, event, handle, *args):
        """
        Bind a handle to an event with *args being appended to the event
        arguments when the event occurs.
        """

        item = self.base.setdefault(event, list())
        item.append((handle, args))
