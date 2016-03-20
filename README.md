untwisted
=========

What is untwisted?

A library for asynchronous programming in python. 

Despite of the above statement being true it doesn't answer the question entirely. Untwisted is a different approach to solve the problem of
implementing networking applications. Untwisted architecture makes it simpler to handle internet protocols, consequently it is easier
to implement applications that run on top of such protocols. 

Untwisted supports asynchronously dealing with sockets, file descriptors while spawning threads to perform other jobs. It is possible to talk
to a process using a thread based approach or a unix file descriptor while waiting for socket's events. Untwisted basically
solves the problem that some python libraries like pexpect and twisted proposes to solve in a neat and powerful way.


### Web Server

~~~python
from untwisted.plugins.rapidserv import RapidServ, core

app = RapidServ(__file__)

@app.request('GET /')
def send_base(con, request):
    con.add_data('<html> <body> <p> Rapidserv </p> </body> </html>')
    con.done()

if __name__ == '__main__':
    app.bind('0.0.0.0', 80, 50)
    core.gear.mainloop()
~~~


### Echo Server

~~~python
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
~~~

### 

### Simple Chat Server

This simple chat permits clients to connect through telnet protocol, pick up a nick then start chatting.

~~~python
"""
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import Stdin, Stdout, Server, ACCEPT, CLOSE, lose
from untwisted.splits import Terminator
from untwisted.tools import coroutine

class ChatServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Terminator(client, delim='\r\n')
        
        xmap(client, CLOSE, self.handle_close)
        client.dump('Type a nick.\r\nNick:')    
        
        client.nick, = yield client, Terminator.FOUND

        xmap(client, Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump('%s:%s\r\n' % (client.nick, data))

    def handle_close(self, client, err):
        lose(client)
        self.pool.remove(client)

if __name__ == '__main__':
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)

    Server(server)
    ChatServer(server)
    core.gear.mainloop()
~~~


### Spawn Processes

The example below spawns a python process then sends a line of code.

~~~python
from untwisted.expect import Expect, LOAD, CLOSE
from untwisted.network import core, xmap, die

def handle(expect, data):
    print data

expect = Expect('python', '-i', '-u')
xmap(expect, LOAD, handle)
xmap(expect, CLOSE, lambda expect: die())
expect.send('print "hello world"\nquit()\n')
core.gear.mainloop()
~~~


