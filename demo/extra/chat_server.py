"""
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import Stdin, Stdout, Server, ACCEPT, CLOSE, lose
from untwisted.splits import Shrug, FOUND
from untwisted.tools import coroutine

class ChatServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Shrug(client, delim='\r\n')
        
        xmap(client, CLOSE, self.handle_close)
        client.dump('Type a nick.\r\nNick:')    
        
        client.nick, = yield client, FOUND

        xmap(client, FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump('%s:%s\r\n' % (client.nick, data))

    def handle_close(self, client, err):
        lose(client)
        self.pool.remove(client)

if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)

    Server(server)
    ChatServer(server)
    core.gear.mainloop()






