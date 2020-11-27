from untwisted.server import create_server
from untwisted.event import ACCEPT, LOAD
from untwisted import core

class EchoServer:
    def __init__(self, server):
        server.add_map(ACCEPT, lambda server, con: 
                     con.add_map(LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()




