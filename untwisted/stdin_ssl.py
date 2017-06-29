from untwisted.stdin import Stdin
from untwisted.dump_ssl import DumpStrSSL, DumpFileSSL

class StdinSSL(Stdin):
    def dump(self, data):
        self.start()
        data = DumpStrSSL(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFileSSL(fd)
        self.queue.append(fd)


