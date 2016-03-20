from untwisted.network import Spin, xmap, core
from untwisted.iostd import Server, Stdout, Stdin, ACCEPT, LOAD, CLOSE, lose

class EchoServer(object):
    def __init__(self, server):
        Server(server)
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, con):
        Stdin(con)
        Stdout(con)
       
        xmap(con, LOAD,  lambda con, data: con.dump(data))
        xmap(con, CLOSE, lambda con, err: lose(con))

if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(200)

    EchoServer(server)
    core.gear.mainloop()






