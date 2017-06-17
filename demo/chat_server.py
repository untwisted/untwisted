"""
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import create_server, ACCEPT, CLOSE, lose
from untwisted.splits import Terminator
from untwisted.tools import coroutine

class ChatServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim='\r\n')
        xmap(client, CLOSE, lambda client, err: self.pool.remove(client))

        client.dump('Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        xmap(client, Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump('%s:%s\r\n' % (client.nick, data))

if __name__ == '__main__':
    server = create_server('', 1234, 5)
    ChatServer(server)
    core.gear.mainloop()



