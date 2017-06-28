from untwisted.dump import DumpStr, DumpFile
from untwisted.stdin import Stdin

class StdinSSL(Stdin):
    def dump(self, data):
        self.start()
        data = DumpStr(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFile(fd)
        self.queue.append(fd)

