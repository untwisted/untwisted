from untwisted.network import xmap, spawn, get_event
from untwisted.utils.stdio import LOAD

BOX = get_event()

class Fixed(object):
    """
    A protocol for fixed chunks.

    It spawns BOX when the accumulator hits the specified
    size in bytes.
    """

    def __init__(self, spin, size=4):
        xmap(spin, LOAD, self.update)

        self.box  = ''
        self.size = size

    def update(self, spin, data):
        self.box = self.box + data

        while len(self.box) >= self.size:
            chunk    = buffer(self.box, 0, 4)
            self.box = buffer(self.box, 4)
            spawn(spin, BOX, chunk)

