"""
"""

from untwisted.network import SuperSocket
from untwisted.sock_reader import SockReader
from untwisted.sock_writer import SockWriter
from untwisted.event import CLOSE, ACCEPT
from untwisted.server import Server
from untwisted.splits import Terminator
from untwisted.tools import handle_exception
from untwisted import core
import operator
from functools import reduce

class CalcParser:
    """
    """

    def __init__(self, client):
        client.add_map(Terminator.FOUND, self.handle_found)

    @handle_exception(ValueError)
    def handle_found(client, data):
        op, args = data.decode('utf8').split(' ', 1)
        args     = list(map(float, args.split(' ')))
        client.drive(op, args)

class CalcServer:
    """ 
    """

    def __init__(self, server):
        server.add_map(ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        SockWriter(client)
        SockReader(client)
        Terminator(client, delim=b'\r\n')
        parser = CalcParser(client)
        
        client.add_map('add', self. on_add)    
        client.add_map('sub', self.on_sub)    
        client.add_map('mul', self.on_mul)    
        client.add_map('div', self.on_div)    
        client.add_map((parser.handle_found, ValueError), self.on_error)    

        client.add_map(CLOSE, self.handle_close)

    def on_add(self, client, args):
        self.send_msg(client, reduce(operator.add, args, 0))

    def on_sub(self, client, args):
        self.send_msg(client, reduce(operator.sub, args, 0))

    def on_div(self, client, args):
        self.send_msg(client, reduce(operator.truediv, args, args.pop(0)))

    def on_mul(self, client, args):
        self.send_msg(client, reduce(operator.mul, args, args.pop(0)))

    def on_error(self, client, excpt):
        self.send_msg(client, excpt)

    def handle_close(self, client, err):
        client.destroy()
        client.close()

    def send_msg(self, client, msg):
        client.dump(('%s\r\n' % msg).encode('utf8'))

if __name__ == '__main__':
    server = SuperSocket()
    server.bind(('', 1234))
    server.listen(5)

    Server(server)
    CalcServer(server)
    core.gear.mainloop()

