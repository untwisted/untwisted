# It imports basic objects.
from untwisted.network import core, Spin, xmap
from untwisted.iostd import Server, Stdin, ACCEPT, CLOSE
from time import asctime

class TimeServ(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
       

    def handle_accept(self, server, con):
        Stdin(con)

        con.dump('%s\r\n' % asctime())
        xmap(con, CLOSE, lambda con, err: lose(con))


if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(200)

    Server(server)
    TimeServ(server)
    core.gear.mainloop()





