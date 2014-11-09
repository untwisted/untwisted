from untwisted.network import *
from untwisted.event import *

class Append:
    def __init__(self, spin):
        self.stream = ''
        self.BLOCK = 1024
        
        xmap(spin, LOAD, self.update)
        spin.append = self 
        #install dump method into spin

    def update(self, spin, data):
        self.stream = self.stream + data 
        spawn(spin, self.stream, data)

