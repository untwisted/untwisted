from untwisted.network import Spin, xmap, core
from untwisted.iostd import Server, Stdout, Stdin, ACCEPT, LOAD, CLOSE

class EchoServer(object):
    def __init__(self, spin):
        xmap(spin, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        Stdin(client)

        Stdout(client)
       
        xmap(client, LOAD, self.handle_load)
        xmap(client, CLOSE, self.handle_close)

    def handle_load(self, client, data):
        client.dump(data)

    def handle_close(self, client, err):
        client.destroy()
        client.close()

if __name__ == '__main__':
    spin = Spin()
    spin.bind(('', 1234))
    spin.listen(200)


    Server(spin)


    EchoServer(spin)
    core.gear.mainloop()




