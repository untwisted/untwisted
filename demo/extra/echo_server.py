from untwisted.network import Spin, xmap, core
from untwisted.iostd import create_server, ACCEPT, LOAD, CLOSE, lose

class EchoServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, con):
        xmap(con, LOAD,  lambda con, data: con.dump(data))
        xmap(con, CLOSE, lambda con, err: lose(con))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()

