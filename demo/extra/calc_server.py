"""
"""

from untwisted.network import core, Spin, xmap, spawn
from untwisted.iostd import Server, Stdin, Stdout, CLOSE, ACCEPT
from untwisted.splits import Shrug, FOUND
import operator

class InvalidExpression(Exception):
    pass

class CalcParser(object):
    """
    """

    def __init__(self, client):
        xmap(client, FOUND, self.handle_found)

    def handle_found(self, client, data):
        op, args = data.split(' ', 1)
        args     = args.split(' ')

        try:
            args = map(float, args)
        except ValueError as e:
            raise InvalidExpression
        else:
            spawn(client, op, args)

class CalcServer(object):
    """ 
    """

    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Shrug(client, delim='\r\n')
        CalcParser(client)
        
        xmap(client, 'add', self. on_add)    
        xmap(client, 'sub', self.on_sub)    
        xmap(client, 'mul', self.on_mul)    
        xmap(client, 'div', self.on_div)    
        xmap(client, InvalidExpression, self.on_error)    

        xmap(client, CLOSE, self.handle_close)

    def on_add(self, client, args):
        self.send_msg(client, reduce(operator.add, args, 0))

    def on_sub(self, client, args):
        self.send_msg(client, reduce(operator.sub, args, 0))

    def on_div(self, client, args):
        self.send_msg(client, reduce(operator.div, args, 1))

    def on_mul(self, client, args):
        self.send_msg(client, reduce(operator.mul, args, 1))

    def on_error(self, client, args):
        self.send_msg(client, 'The expression is invalid!')

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


