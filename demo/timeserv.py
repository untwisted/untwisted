# It imports basic objects.
from untwisted.network import SuperSocket
from untwisted.server import Server, ACCEPT
from untwisted.client import lose, CLOSE
from untwisted.sock_writer import SockWriter
from untwisted.sock_reader import SockReader
from untwisted import core
from time import asctime

class TimeServ:
    def __init__(self, server):
        server.add_map(ACCEPT, self.handle_accept)

    def handle_accept(self, server, con):
        SockWriter(con)
        SockReader(con)

        con.dump(('%s\r\n' % asctime()).encode('utf-8'))
        con.add_map(CLOSE, lambda con, err: lose(con))


if __name__ == '__main__':
    server = SuperSocket()
    server.bind(('', 1234))
    server.listen(200)

    Server(server)
    TimeServ(server)
    core.gear.mainloop()








