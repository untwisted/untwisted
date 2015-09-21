# It imports basic objects.
from untwisted.network import *
from untwisted.utils.stdio import *
from time import asctime

class TimeServ(object):
    def __init__(self, server):
        # It is basically server.link.
        xmap(server, ACCEPT, self.handle_accept)
       

    def handle_accept(self, server, con):
        """ When cons connect we are called. """
        Stdin(con)
        Stdout(con)

        con.dump('%s\r\n' % asctime())
        xmap(con, CLOSE, lambda con, err: lose(con))


if __name__ == '__main__':
    # We create a Spin class pretty much as we would
    # do with a socket class.
    server = Spin()
    server.bind(('', 1234))
    server.listen(200)

    Server(server)
    TimeServ(server)
    core.gear.mainloop()




