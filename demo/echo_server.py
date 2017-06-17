from untwisted.network import Spin, xmap, core
from untwisted.iostd import create_server, ACCEPT, LOAD

class EchoServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()


