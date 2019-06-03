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
~~~

### 

### Chat Server

~~~python
~~~


### Spawn Processes

The example below spawns a python process then sends a line of code.

~~~python
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

Documentation
=============

[Wiki](https://github.com/iogf/untwisted/wiki)

Support
=======

#### Freenode

**Address:** irc.freenode.org

**Channel:** #untwisted
 


