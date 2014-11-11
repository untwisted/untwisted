from untwisted.network import core, xmap, cmap, READ, WRITE, spawn, zmap
from untwisted.utils.stdio import DUMPED, CLOSE, LOAD
from collections import deque

class Stdin(object):
    """
    A protocol for sending data through a device.
    """


    def __init__(self, device):
        self.device = device
        device.dump = self.dump
        self.queue  = deque()


    def dump(self, data):
        """
        It sends data asynchronously through the device.
        """

        self.queue.append(data)
        xmap(self.device, WRITE, self.update)

    def update(self, device):
        try:
            data = self.queue.popleft()
        # As device.write returns None
        # we don't need to worry whether it has sent all the bytes
        # unlike with sockets.
            device.write(data)
        except IndexError:
        # When the queue is empty then we don't need
        # the WRITE event.
            zmap(device, WRITE, self.update)
            spawn(device, DUMPED)
        except IOError as excpt:
        # If something went wrong it spawns CLOSE with err.
        # The err parameter gives a clue of what happened.
            err = excpt.args[0]
            spawn(device, CLOSE, err)


class Stdout(object):
    """
    A protocol for reading data from a device.
    """

    def __init__(self, device):
        xmap(device, READ, self.update)

    def update(self, device):
        try:
            data = device.read()
            spawn(device, LOAD, data)
        except IOError as excpt:
        # If something went wrong it spawns CLOSE with err.
            err = excpt.args[0]
            spawn(device, CLOSE, err)

def lose(device):
    """
    It is used to close the device and destroy the Device instance.
    """
    device.destroy()
    device.close()



