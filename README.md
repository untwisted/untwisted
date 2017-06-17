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

class EchoServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, lambda server, con: 
                     xmap(con, LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()
~~~

### 

### Chat Server

This simple chat server permits clients to connect through telnet protocol, 
pick up a nick then start chatting.

~~~python
from untwisted.network import core, Spin, xmap
from untwisted.iostd import create_server, ACCEPT, CLOSE, lose
from untwisted.splits import Terminator
from untwisted.tools import coroutine

class ChatServer(object):
    def __init__(self, server):
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim='\r\n')
        xmap(client, CLOSE, lambda client, err: self.pool.remove(client))

        client.dump('Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        xmap(client, Terminator.FOUND, self.echo_msg)
        self.pool.append(client)

    def echo_msg(self, client, data):
        for ind in self.pool:
            if not ind is client:
                ind.dump('%s:%s\r\n' % (client.nick, data))

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
    print data

expect = Expect('python', '-i', '-u')
xmap(expect, LOAD, handle)
xmap(expect, CLOSE, lambda expect: die())
expect.send('print "hello world"\nquit()\n')
core.gear.mainloop()
~~~

Install
=======

Untwisted depends on python2.

    pip install untwisted


Documentation
=============

[Wiki](https://github.com/iogf/untwisted/wiki)


Applications using Untwisted
============================

#### [Vy](https://github.com/iogf/vy)

A vim-like in python made from scratch.

#### [Ameliabot](https://github.com/iogf/ameliabot)

A flexible ircbot written on top of untwisted framework.

#### [Steinitz](https://github.com/iogf/steinitz)

A chess interface to fics with support for stockfish to analyze moves.

Support
=======

#### Freenode

**Address:** irc.freenode.org

**Channel:** #untwisted
 




