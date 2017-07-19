from builtins import object
from untwisted.core import Kill, Root
from untwisted.exceptions import Stop, Erase
from untwisted.debug import debug

class Dispatcher(object):
    """
    The event dispatcher class.
    """

    def __init__(self):
        self.base = dict()
        self.pool = list()
        self.step = list()

    def drive(self, event, *args):
        """
        Used to dispatch events.
        """

        maps = self.base.get(event, self.step)
        for handle, data in maps[:]:
            params = args + data
            try:
                handle(self, *params)
            except Stop:
                break
            except StopIteration:
                pass
            except Kill as Root:
                raise
            except Erase:
                maps.remove((handle, data))
            except Exception as e:
                debug(event, params)

        for handle in self.pool:
            handle(self, event, args)

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
            self.base[event] = [ind for ind in self.base[event] if ind[0] != handle]

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

    def del_step(self, handle):
        """
        """

        self.step.remove(handle)

    def add_step(self, handle):
        """
        """

        self.step.append(handle)




