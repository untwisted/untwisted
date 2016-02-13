from untwisted.network import core, xmap, cmap, READ, WRITE, spawn, zmap
from untwisted.event import DUMPED, CLOSE, LOAD
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
        except IndexError:
            zmap(device, WRITE, self.update)
            spawn(device, DUMPED)
        except IOError as excpt:
            err = excpt.args[0]
            spawn(device, CLOSE, err)
        else:
            device.write(data)

class Stdout(object):
    """
    A protocol for reading data from a device.
    """

    def __init__(self, device):
        xmap(device, READ, self.update)

    def update(self, device):
        try:
            data = device.read()
        except IOError as excpt:
            err = excpt.args[0]
            spawn(device, CLOSE, err)
        else:
            spawn(device, LOAD, data)

def lose(device):
    """
    It is used to close the device and destroy the Device instance.
    """
    device.destroy()
    device.close()





