"""
"""

from untwisted.network import core, Spin, xmap, spawn
from untwisted.iostd import Server, Stdin, Stdout, CLOSE, ACCEPT
from untwisted.splits import Terminator
from untwisted.tools import handle_exception
import operator

class CalcParser(object):
    """
    """

    def __init__(self, client):
        xmap(client, Terminator.FOUND, self.handle_found)

    @handle_exception(ValueError)
    def handle_found(client, data):
        op, args = data.split(' ', 1)
        args     = map(float, args.split(' '))
        spawn(client, op, args)

class CalcServer(object):
    """ 
    """

    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Terminator(client, delim='\r\n')
        parser = CalcParser(client)
        
        xmap(client, 'add', self. on_add)    
        xmap(client, 'sub', self.on_sub)    
        xmap(client, 'mul', self.on_mul)    
        xmap(client, 'div', self.on_div)    
        xmap(client, (parser.handle_found, ValueError), self.on_error)    

        xmap(client, CLOSE, self.handle_close)

    def on_add(self, client, args):
        self.send_msg(client, reduce(operator.add, args, 0))

    def on_sub(self, client, args):
        self.send_msg(client, reduce(operator.sub, args, 0))

    def on_div(self, client, args):
        self.send_msg(client, reduce(operator.div, args, args.pop(0)))

    def on_mul(self, client, args):
        self.send_msg(client, reduce(operator.mul, args, args.pop(0)))

    def on_error(self, client, excpt):
        self.send_msg(client, excpt)

    def handle_close(self, client, err):
        client.destroy()
        client.close()

    def send_msg(self, client, msg):
        client.dump('%s\r\n' % msg)

if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)

    Server(server)
    CalcServer(server)
    core.gear.mainloop()





