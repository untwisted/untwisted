from untwisted.network import *
from untwisted.utils.stdio import LOAD
FOUND = get_event()

class Shrug:
    def __init__(self, spin, delim='\r\n'):
        self.delim = delim
        self.msg = bytearray()

        xmap(spin, LOAD, self.update)

    def update(self, spin, data):
        self.msg.extend(data)
        if self.delim in data:
            chain = self.msg.split(self.delim)
            self.msg = chain[-1]
            del chain[-1]

            for ind in chain:
            # I'm not sure if i should just pass ind.
                spawn(spin, FOUND, str(ind))

                


