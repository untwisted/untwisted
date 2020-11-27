Untwisted
=========

Untwisted is an event driven framework meant to implement networking applications using
non blocking sockets.

Untwisted supports asynchronously dealing with sockets, spawning processes while spawning threads to 
perform other jobs. It is possible to talk to a process using a thread based approach or a unix file 
descriptor while waiting for socket's events. Untwisted basically solves the problem that some Python 
libraries like pexpect and twisted proposes to solve in a flexible but concrete manner.

Untwisted implements the concept of super sockets. A super socket in the untwisted context it is an event emitter
system. Those who are familiar with Nodejs would feel more comfortable with untwisted super sockets approach.

A SuperSocket instance is a socket with an event dispatcher mechanism. Handles can be mapped to events
that are called when a given event associated with the socket happens.

~~~python
from untwisted.network import SuperSocket
from untwisted.client import Client
from untwisted.event import CONNECT, CONNECT_ERR
from untwisted import core

def handle_connect(ssock):
    print('Connected !')

def handle_connect_err(ssock, err):
    print('Not connected:', err)

ssock = SuperSocket()
# An extesion that is responsible for spawning CONNECT or CONNECT_ERR events.
Client(ssock)
ssock.connect_ex(('httpbin.org', 80))

# When the client connects just call handle_connect.
ssock.add_map(CONNECT, handle_connect)

# In case it fails just call handle_connect_err.
ssock.add_map(CONNECT_ERR, handle_connect_err)

# Start the reactor.
core.gear.mainloop()
~~~


Events can be spawned from event handles thus allowing different parts of an application to raise
new events. Events can be any kind of Python objects, strings, integers etc.

The event-driven paradigm is such a powerful mean of handling many problems in the asynchronicity
world however it might become too harsh sometimes. Untwisted  attempts to simplify working with internet
protocols thus building networking applications.

### Echo Server

This code implements a basic echo server.

~~~python
from untwisted.event import ACCEPT, LOAD
from untwisted import core

class EchoServer:
    def __init__(self, server):
        server.add_map(ACCEPT, lambda server, con: 
                     con.add_map(LOAD, lambda con, data: con.dump(data)))

if __name__ == '__main__':
    EchoServer(create_server('0.0.0.0', 1234, 5))
    core.gear.mainloop()
~~~

### Chat Server

This piece of code just sets up a simple telnet chat. Once the code
is running just connect on port 1234 via telnet, type a nick and start chatting :)

~~~python
from untwisted.server import create_server
from untwisted.event import ACCEPT, CLOSE
from untwisted.splits import Terminator
from untwisted.tools import coroutine
from untwisted import core

class ChatServer:
    def __init__(self, server):
        server.add_map(ACCEPT, self.handle_accept)
        self.pool = []

    @coroutine
    def handle_accept(self, server, client):
        Terminator(client, delim=b'\r\n')
        client.add_map(CLOSE, lambda client, err: self.pool.remove(client))

        client.dump(b'Type a nick.\r\nNick:')    
        client.nick, = yield client, Terminator.FOUND

        client.add_map(Terminator.FOUND, self.echo_msg)
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


### Spawn Process

Untwisted allows you to spawn processes send/read data asynchronously. The example below
spawns a Python interpreter instance. The code is sent to the interpreter and output
is read both from the process stdout and stderr.

~~~python
from untwisted.expect import ChildStdout, ChildStderr, ChildStdin
from subprocess import Popen, PIPE
from untwisted.event import LOAD, CLOSE
from untwisted.core import die
from untwisted import core


def on_stdout(stdout, data):
    print('Stdout data: ', data)

def on_stderr(stderr, data):
    print('Stderr data:', data)

def on_close(expect):
    print('Closing..')
    die()

if __name__ == '__main__':
    code = b'print("hello world")\nprint(1/0)\nquit()\n'

    proc   = Popen(['python', '-i', '-u'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdin  = ChildStdin(proc)
    stdout = ChildStdout(proc)
    stderr = ChildStderr(proc)
    
    stdin.send(code)
    stdout.add_map(LOAD, on_stdout)
    stderr.add_map(LOAD, on_stderr)
    stdout.add_map(CLOSE, on_close)
    core.gear.mainloop()
~~~

Would output:

~~~
(untwisted) [tau@localhost demo]$ python spawn_process.py 
Stderr data: b'Python 3.9.0 (default, Oct  6 2020, 00:00:00) \n'
Stderr data: b'[GCC 10.2.1 20200826 (Red Hat 10.2.1-3)] on linux\n'
Stderr data: b'Type "help", "copyright", "credits" or "license" for more information.\n'
Stdout data:  b'hello world\n'
Stderr data: b'>>> >>> Traceback (most recent call last):\n'
Stderr data: b'  File "<stdin>", line 1, in <module>\n'
Stderr data: b'ZeroDivisionError: division by zero\n'
Closing..
~~~

Install
=======

Untwisted would run on python3.

    pip install untwisted


Documentation
=============

[Untwisted Book](https://github.com/untwisted/untwisted/wiki)

Applications using Untwisted
============================

#### [Sukhoi](https://github.com/untwisted/sukhoi)

A powerful micro Web Crawling Framework.

#### [Vy](https://github.com/vyapp/vy)

A vim-like in python made from scratch.

#### [Ameliabot](https://github.com/untwisted/ameliabot)

A flexible ircbot written on top of untwisted framework.

#### [Steinitz](https://github.com/untwisted/steinitz)

A chess interface to fics with support for stockfish to analyze moves.

#### [Websnake](https://github.com/untwisted/websnake)

Asynchronous web requests in python.

#### [Rapidserv](https://github.com/untwisted/rapidserv)

A non-blocking Flask-like Web Framework in python.
