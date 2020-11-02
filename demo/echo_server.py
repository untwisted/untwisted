from untwisted.network import xmap, core
from untwisted.server import create_server
from untwisted.event import ACCEPT, LOAD

class EchoServer:
    def __init__(self, server):
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()




