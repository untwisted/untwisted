from untwisted.network import xmap
from untwisted.utils.stdio import LOAD

class Accumulator(object):
    """
    Just an accumulator on LOAD.
    """
    def __init__(self, spin):
        xmap(spin, LOAD, self.update)
        spin.accumulator = self
        self.data = ''

    def update(self, spin, data):
        self.data = self.data + data


