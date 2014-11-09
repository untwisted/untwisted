from untwisted.network import *
from untwisted.utils.stdio import LOAD
FOUND = get_event()

class Shrug:
    def __init__(self, spin, delim='\r\n'):
        self.delim = delim
        self.stream = ''

        xmap(spin, LOAD, self.update)

    def update(self, spin, data):
        if self.delim in data:
            chunk = self.stream + data
            chain = chunk.split(self.delim)
            self.stream = chain[-1]
            del chain[-1]

            for ind in chain:
                spawn(spin, FOUND, ind)

        else:
            self.stream = self.stream + data
                

