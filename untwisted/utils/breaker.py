from untwisted.network import core, xmap, cmap, READ, WRITE, spawn
from untwisted.core import get_event
from untwisted.utils.shrug import FOUND

class Breaker(object):
    def __init__(self, device, delim=' '):
        self.delim = delim
        xmap(device, FOUND, self.handle_found)

    def handle_found(self, device, data):
        tokens = data.split(self.delim, 4)
        event = tokens[0]
        del tokens[0]
        spawn(device, event, *tokens)





