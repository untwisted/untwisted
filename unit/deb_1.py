""" deb_1.py 
    Usage: Used to test hold object functionality.
    It uses the /demo/echo/echo.py to send commands and wait for them
    using hold object.
"""
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *

def main():
    for ind in xrange(100):
        sock = socket(AF_INET, SOCK_STREAM)
        spin = Spin(sock)
        Client(spin)
        Stdin(spin)
        Stdout(spin)
        Shrug(spin)
        spin.connect_ex(('', 1234))
        xmap(spin, FOUND, split)
        xmap(spin, CONNECT, on_connect, ind)
        xmap(spin, CONNECT_ERR, on_connect_err, ind)


def split(spin, data):
    spawn(spin, data)

def on_connect(spin, counter):
    spin.dump('cmd_x\r\n')
    print 'Waiting for cmd_x from, ', counter
    event, args = yield hold(spin, 'cmd_x')
    print 'cmd_x arrived from, ', counter
    spin.dump('cmd_y\r\n')
    print 'Waiting for cmd_y from, ', counter
    event, args = yield hold(spin, 'cmd_y')
    print 'cmd_y arrived from, ', counter

def on_connect_err(spin, ind):
    print 'Error connect from, ', ind
    pass

if __name__ == '__main__':
    main()
    core.gear.mainloop()
