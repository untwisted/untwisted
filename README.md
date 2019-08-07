Untwisted
=========

What is untwisted?

A library for asynchronous programming in python. 

Despite of the above statement being true it doesn't answer the question entirely. 
Untwisted is a different approach to solve the problem of implementing networking applications. 
Untwisted architecture makes it simpler to handle internet protocols, consequently it is easier
to implement applications that run on top of such protocols. 

Untwisted supports asynchronously dealing with sockets, file descriptors while spawning threads to 
perform other jobs. It is possible to talk to a process using a thread based approach or a unix file 
descriptor while waiting for socket's events. Untwisted basically solves the problem that some python 
libraries like pexpect and twisted proposes to solve in a neat and powerful way.

Untwisted is extremely modular, applications that are implemented on top of untwisted tend to be 
succint and elegant. Untwisted has an impressive performance when compared to other python frameworks.

You may be wondering right now why you would endevour to learn a new python asynchronous framework once 
you have spent so many hours trying to learn asynchronous programming in python with other frameworks. 
One of the reasons to learn untwisted framework is the fact that you'll spend some pleasant hours 
understanding untwisted and some minutes implementing complex applications on top of it. Another reason is
that if you like clean, consistent and high performance code then untwisted is for you.


### Echo Server

This neat piece of code implements a basic echo server.

~~~python
from untwisted.network import Spin, xmap, core
from untwisted.iostd import create_server, ACCEPT, LOAD

class EchoServer:
    def __init__(self, server):
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()
~~~

### Chat Server

This piece of code just sets up a simple telnet chat. Once the code
is running just connect on port 1234 via telnet, type a nick and start chatting :)

~~~python
from untwisted.network import core, Spin, xmap
from untwisted.iostd import create_server, ACCEPT, CLOSE, lose
from untwisted.splits import Terminator
from untwisted.tools import coroutine

class ChatServer:
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim=b'\r\n')
        xmap(client, CLOSE, lambda client, err: self.pool.remove(client))

        client.dump(b'Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        xmap(client, Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump(b'%s:%s\r\n' % (client.nick, data))

if __name__ == '__main__':
    server = create_server('', 1234, 5)
    ChatServer(server)
    core.gear.mainloop()
~~~


### Spawn Processes

The example below spawns a python process then sends a line of code.

~~~python
from untwisted.expect import Expect, LOAD, CLOSE
from untwisted.network import core, xmap, die

def handle(expect, data):
    print(data)

def on_close(expect):
    print('Closing..')
    die()

expect = Expect('python', '-i', '-u')

expect.send(b'print("hello world");quit();\n\n')

xmap(expect, LOAD, handle)
xmap(expect, CLOSE, on_close)

core.gear.mainloop()
~~~

Install
=======

Untwisted would run on python3.

    pip install untwisted


Documentation
=============

[Wiki](https://github.com/iogf/untwisted/wiki)


Applications using Untwisted
============================

#### [Sukhoi](https://github.com/untwisted/sukhoi)

A powerful micro Web Crawling Framework.

#### [Vy](https://github.com/iogf/vy)

A vim-like in python made from scratch.

#### [Ameliabot](https://github.com/iogf/ameliabot)

A flexible ircbot written on top of untwisted framework.

#### [Steinitz](https://github.com/iogf/steinitz)

A chess interface to fics with support for stockfish to analyze moves.

#### [Websnake](https://github.com/iogf/websnake)

Asynchronous web requests in python.

#### [Rapidserv](https://github.com/iogf/rapidserv)

A non-blocking Flask-like Web Framework in python.

Support
=======

#### Freenode

**Address:** irc.freenode.org

**Channel:** #untwisted
 





