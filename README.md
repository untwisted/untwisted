untwisted
=========

What is untwisted?

A library for asynchronous programming in python. 

Despite of the above statement being true it doesn't answer the question entirely. Untwisted is a different approach to solve the problem of
implementing networking applications. Untwisted architecture makes it simpler to handle internet protocols, consequently it is easier
to implement applications that run on top of such protocols. 

Untwisted supports asynchronously dealing with sockets,, file descriptors and yet spawn threads to perform other jobs. It is possible to talk
to a process using a thread based approach or a unix file descriptor while waiting for socket's events. Untwisted basically
solves the problem that some python libraries like pexpect and twisted proposes to solve in a neat and powerful way.




