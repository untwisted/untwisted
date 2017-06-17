from untwisted.network import core, xmap, Device
from untwisted.iofile import *
from subprocess import Popen, PIPE, STDOUT
from untwisted.core import Kill

def on_close(dev, err):
    print 'On CLOSE ...', err
    lose(dev)
    raise Kill

def on_load(dev, data):
    print 'On LOAD ...', data

child   = Popen(['python2', '-i'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)

stdout  = Device(child.stdout)
stdin   = Device(child.stdin)

Stdin(stdin)
Stdout(stdout)

stdin.dump('print "hello world!"\n')
xmap(stdin, DUMPED, lambda dev: stdin.dump('quit()\n'))
xmap(stdout, LOAD, on_load)
xmap(stdin, CLOSE, on_close)
xmap(stdout, CLOSE, on_close)

core.gear.mainloop()


