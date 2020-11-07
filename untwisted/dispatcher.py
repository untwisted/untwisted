from untwisted.core import Kill, Root
from untwisted.debug import debug

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

    def add_map(self, event, handle, *args):
        """
        Add a mapping.
        """

        item = self.base.setdefault(event, list())
        item.append((handle, args))

    def clear_maps(self, event, handle, *args):
        pass

    def del_map(self, event, handle, *args):
        """
        Remove a mapping.
        """

        self.base[event].remove((handle, args))

    def once(self, event, handle, *args):
        """
        """
    
        def shell(*args):
            try:
                handle(self, *args)
            except Exception as e:
                raise e
            finally:
                self.del_map(event, shell)
        self.add_map(event, shell, *args)
    
    def install_maps(self, *args):
        """
        Install a set of mappings.
        """

        for ind in args:
            self.add_map(*ind)

    def insert_map(self, index, handle):
        """

        """

        pass


