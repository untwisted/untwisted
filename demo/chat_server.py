"""
"""

from untwisted.server import create_server
from untwisted.event import ACCEPT, CLOSE
from untwisted.splits import Terminator
from untwisted.tools import coroutine
from untwisted import core

class ChatServer:
    def __init__(self, server):
        server.add_map(ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim=b'\r\n')
        client.add_map(CLOSE, lambda client, err: self.pool.remove(client))

        client.dump(b'Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        client.add_map(Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump(b'%s:%s\r\n' % (client.nick, data))

if __name__ == '__main__':
    server = create_server('', 1234, 5)
    ChatServer(server)
    core.gear.mainloop()





