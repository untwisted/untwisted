from untwisted.network import core, xmap, Device
from untwisted.iofile import *
from subprocess import Popen, PIPE, STDOUT
from untwisted.core import Kill
from os import environ, setsid, killpg

def on_close(dev, err):
    print 'On CLOSE ...', err
    lose(dev)
    raise Kill

def on_load(dev, data):
    print 'On LOAD ...', data

child   = Popen(['python2', '-i'], stdout=PIPE, stdin=PIPE, 
                     preexec_fn=setsid, stderr=STDOUT,  env=environ)

stdout  = Device(child.stdout)
stdin   = Device(child.stdin)

Stdin(stdin)
Stdout(stdout)

stdin.dump('print "hello world"\n')
stdin.dump('quit()\n')
xmap(stdin, DUMPED, lambda dev: stdin.dump('print "foo"\n'))
xmap(stdout, LOAD, on_load)
xmap(stdin, CLOSE, on_close)
xmap(stdout, CLOSE, on_close)

core.gear.mainloop()

