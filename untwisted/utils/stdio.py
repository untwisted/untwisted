from untwisted.network import Spin, spawn, xmap, zmap, get_event, READ, WRITE
from untwisted.usual import debug
from collections import deque
import socket

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
ENOTCONN, ESHUTDOWN, EINTR, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN 

CLOSE_ERR_CODE   = (ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE, EBADF)
ACCEPT_ERR_CODE  = (EWOULDBLOCK, ECONNABORTED, EAGAIN)
CLOSE            = get_event()
ACCEPT           = get_event()
CONNECT          = get_event()
CONNECT_ERR      = get_event()
LOAD             = get_event()
DUMPED           = get_event()
RECV_ERR         = get_event()
SEND_ERR         = get_event()
ACCEPT_ERR       = get_event()
READ_ERR         = get_event()
DUMPED_FILE      = get_event()
CLOSE_ERR        = get_event()


class Stdin:
    """ 
    This class implements a protocol that manages
    the sending of data. The method 'dump' is used to append 
    a chunk of text on top of a queue.
    
    Whenever we are ready to write 'update' method pops a chunk of data 
    from the queue and tries to send as many bytes as possible from this chunk. 
    
    When a chunk is fully sent it starts sending the next chunk and so on.

    Dependencies: NONE

    Event: CLOSE 
    Args: spin, err
    
    When a call to send is done it might throw an exception that carries
    a value to mean what occured. It might be the case that the connection
    is closed. If such an exception carries one of the values defined in 
    CLOSE_ERR_CODE as shown below it means the connection is closed.

    CLOSE_ERR_CODE = (ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE, EBADF)
    
    The spin is the socket instance where the event occured, err is
    the socket status value meaning the motive by which the connection
    was closed. The value err is defined in the standard python module
    errno. 

    import errno
    errno.errorcode[err]    # It just prints the string name for the error.

    Event: SEND_ERR 
    Args: spin, err
    Description: It might occur some error and it doesn't mean the connection
    is closed. So, SEND_ERR carries the value err meaning what occured with
    the call to send.

    Event: DUMPED
    Args: spin 
    Description: This event occurs when the protocol has finished to send all data
    that was appended to the queue. It is, when the queue is empty
    Stdin spawns DUMPED.

    # Name: foo.py
    # Description: This example connects to a local socket it sends
    # a chunk of text and disconnects.

    from untwisted.network import xmap, Spin, core
    from untwisted.utils.stdio import Client, Stdin, CONNECT, DUMPED, lose
    from socket import *

    def set_up_con(con):
    # We install Stdin to be able of sending data.
        Stdin(con)
    # When everything is sent it just disconnects.
        xmap(con, DUMPED, lose)

    # Stdin installs dump method in con. 
    # So, we can use it to send data.
        con.dump('Hello world\r\n')

    sock = socket(AF_INET, SOCK_STREAM)
    con = Spin(sock)
    Client(con)
    con.connect_ex(('localhost', 1234))
    xmap(con, CONNECT, set_up_con)

    core.gear.mainloop()

    """

    def __init__(self, spin):
        """ It initializes basic structures and installs dump into spin. """

        self.queue = deque()
        self.spin = spin 
        self.data = ''
        
        # Install dump method into spin.
        spin.dump = self.dump

    def update(self, spin):
        """
            This method is called on WRITE to send data.
            It attempts to optmize the job of sending bytes by using
            buffer. 
            
            The algorithm is explained in the class doc.

            Events: DUMPED, CLOSE, SEND_ERR

            See help(Stdin).
        """

        try:
            if not self.data:
                self.data = self.queue.popleft()

        # As we are in non blocking mode a call to send
        # doesn't block. We just need to know the amount
        # of bytes sent.
            size = spin.send(self.data)  

        # We move the pointer size bytes ahead.
            self.data = buffer(self.data, size)
        except socket.error as excpt:
            err = excpt.args[0]

        # The err value contains the socket status error code.
        # It is passed with either CLOSE or SEND_ERR so
        # users of this protocol can know what happened
        # exactly with the call to send.
            if err in CLOSE_ERR_CODE:
                spawn(spin, CLOSE, err)
            else:
                spawn(spin, SEND_ERR, err)
                debug()

        except IndexError: 
        # If the queue is empty we no more need
        # the WRITE event.
            zmap(spin, WRITE, self.update)

        # It is important to know when all data was
        # fully sent. It spawns DUMPED when the queue
        # is empty.
            spawn(spin, DUMPED)

    def dump(self, data):
        # If the queue is empty we maps it WRITE
        # otherwise it is already mapped.
        if not self.queue:
           xmap(self.spin, WRITE, self.update)

        # Addes it to be sent.
        self.queue.append(buffer(data))




class Stdout(object):
    """

    This protocol spawns events based on READ event.
    Most protocols will rely on this protocol to know
    when data has arrived.
    
    Dependencies: NONE

    Event: LOAD
    Args: spin, data

    The spin is the socket that data was read from. The data
    is a chunk of bytes that was read from the socket.
    
    Event: CLOSE
    Args: spin, err
    Description: When a call to recv is done it might throw an exception
    as it happens with a call to send such an exception will carry a status value
    for the socket. See help(Stdin) and CLOSE_ERR_CODE to know of the values 
    meaning that the connection is closed. If a call to recv returns ''
    the err will contain ''.

    Event: RECV_ERR
    Args: spin, err
    Description: It might not be the case of the connection being closed
    so it spawns RECV_ERR carrying the status value in err.



    # Name: bar.py
    # Description: It sets a server socket and prints everything 
    # the clients send to the server.

    from untwisted.network import xmap, Spin, core
    from untwisted.utils.stdio import Server, Stdout, lose, ACCEPT, LOAD, CLOSE
    from socket import *
    import sys

    def set_up_con(server, con):
        Stdout(con)
        xmap(con, CLOSE, lambda con, err: lose(con))
        xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\n' % data))
        
    sock = socket(AF_INET, SOCK_STREAM)
    server = Spin(sock) 
    server.bind(('', 1234))
    server.listen(2)
    Server(server)

    xmap(server, ACCEPT, set_up_con)

    core.gear.mainloop()
    
    """
    
    # The max amount of data that is read.
    SIZE = 1024 * 124

    def __init__(self, spin):
        """
        It maps READ to self.update so whenever
        there is data available we can read from the socket.
        """

        # Maps READ to self.update.
        xmap(spin, READ, self.update)

        # Send 1024 bytes at most.

    def update(self, spin):
        """ This method is called on READ to recv
        data from the socket. 

        Events: LOAD, CLOSE, RECV_ERR
        """

        try:
        # Receive self.SIZE bytes at most.
            data = spin.recv(self.SIZE)

        # If data == '' then it is over.
            if not data: spawn(spin, CLOSE, '') 

        # Otherwise it arose data.
            else: spawn(spin, LOAD, data)
        except socket.error as excpt:
            # The excpt.args[0] contains the socket
            # status.
            err = excpt.args[0]

            # If it is the case of the connection being closed
            # we spawn CLOSE with the motive.
            if err in CLOSE_ERR_CODE:
                spawn(spin, CLOSE, err)
            else:
        # In case of error.
                spawn(spin, RECV_ERR, err)
                debug()




class Client(object):
    """
        The order in which protocols are installed is sometimes important
        to have the events propagated in the correct order. Untwisted calls handles
        sequentially, it is the order in which they were mapped to events. So, it is
        important that this protocol be installed before any other protocol is installed
        otherwise you might end up with some odd behavior.
        
        Event: CONNECT
        Args: spin
        Description: This event is spawned when a socket is connected.
        Once CONNECT is issued on a socket it no more spawns CONNECT.
        The idea behind this protocol is having a mean of knowing when a call
        to connect_ex or connect was succesful.



        Event: CONNECT_ERR
        Args: spin, err
        Description: If it isn't the case that the connection was stablished
        the socket will be in a state whose value is non zero. The err
        will contain the motive by which the connection couldn't be stablished.
        See python errno module to know which string name err corresponds to.

        For an example of using this protocol see help(Stdin)
    """

    def __init__(self, spin):
        """
        It installs self.update on WRITE. A call a select with this socket
        in the writting list of sockets would succed if the socket is connected.

        """

        xmap(spin, WRITE, self.update)

    def update(self, spin):
        # All linked to CONNECT is called.
        err = spin.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        
        # If the err is non zero the socket is in error.
        if err != 0:
            spawn(spin, CONNECT_ERR, err)
        else:
            spawn(spin, CONNECT)
        # As we can connect just once, it unlinks self.update from 
        # WRITE.
            zmap(spin, WRITE, self.update)
        # Since it is not going to connect again
        # we just remove it.

class Server(object):
    """
        This protocol is used with listening sockets. 
        It shouldn't be installed in non listening sockets.

        Event: ACCEPT
        Args: spin, new

        The ACCEPT event carries the server socket(spin) and new(the client connected)

        Event: ACCEPT_ERR
        Args: spin, err

        If an attempts to accept fails it throws an exception and the
        standard error is carried with ACCEPT_ERR meaning what happened.

        For an example of usage see help(Stdout)
    """
    def __init__(self, spin):

        # It means it arose a client.
        xmap(spin, READ, self.update)

    def update(self, spin):
        # Calls repeatedly accept to improve efficience.
        while True:
            try:
                sock, addr = spin.accept()

        # Instantiate a new Spin and spreads it.
        # Since it is connected is_on=True
                new = Spin(sock)
                spawn(spin, ACCEPT, new)
                
            except socket.error as excpt:
        # If there is no client accept throws 
        # an exception that is spreaded too.
                err = excpt.args[0]
                if not err in ACCEPT_ERR_CODE:
        # It spawns ACCEPT_ERR just if the socket
        # it isn't a peculiar set of conditions.
        # As we are calling accpet inside a while
        # we would have continously EAGAIN, EWOULDBLOCK etc.
                    spawn(spin, ACCEPT_ERR, err)
                    debug()
                else:
                    break



class Read(object):
    """
    This class is used to read data from a Device.     
    """

    # The amount of data that is gonna be read.
    SIZE = 1024 * 124

    def __init__(self, device):
        xmap(device, READ, self.update)

    def update(self, device):
        try:
        # It might happen of data having length lower than SIZE.
            data = device.read(self.SIZE)
        except IOError as excpt:
        # When an exception occurs it deliveries the exception err.
        # It as well spawns CLOSE.
            err = excpt.args[0]
            spawn(device, CLOSE, err)
        # This is interesting so we can know what is going on.
            debug()
        else:
            if not data: spawn(device, CLOSE, '')
        # The event carrying the data.
        # This is interesting sharing the LOAD event
        # since we can use sub protocols for Stdout.
            spawn(device, LOAD, data)


class Write(object):
    """
    This class is used to write data through a Device.
    """

    def __init__(self, device):
        xmap(device, WRITE, self.update)
        device.dump = self.dump
        self.device = device
        self.queue  = deque()

    def update(self, device):
        try:
            data = self.queue.popleft()
            device.write(data)  
        except IOError as excpt:
            err = excpt.args[0]
            spawn(device, CLOSE, err)
            debug()

        except IndexError: 
        # If the queue is empty we no more need
        # the WRITE event.
            zmap(device, WRITE, self.update)
        # It is important to know when all data was
        # fully sent. It spawns DUMPED when the queue
        # is empty.
            spawn(device, DUMPED)

    def dump(self, data):
        # If the queue is empty we map it to WRITE
        # otherwise it is already mapped.
        if not self.queue:
           xmap(self.device, WRITE, self.update)
        # Addes it to be sent.
        self.queue.append(data)




class DumpFile(object):
    """
    Event: SEND_ERR 
    Args: spin, err
    Description: It might occur some error and it doesn't mean the connection
    is closed. So, SEND_ERR carries the value err meaning what occured with
    the call to send.

    Event: DUMPED
    Args: spin 
    Description: This event occurs when the protocol has finished to send all data
    that was appended to the queue. It is, when the queue is empty
    DumpFile spawns DUMPED.

    Event: READ_ERR
    Args: spin, err
    Description: This event is spawned when an error occurs when reading from 
    a file.

    The user of this class can check how many bytes were sent by just
    checking the fd.tell(). Then determine whether the file was completely
    sent or not.
    """

    def __init__(self, spin, fd):
        self.fd    = fd
        self.data  = ''
        
        self.BLOCK = 1024 * 124

        # It maps WRITE to self.update.
        # Whenever WRITE occurs self.update runs.

        # Install dump method into spin.
        xmap(spin, WRITE, self.update)

    def update(self, spin):
        try:
        # If self.data is '' we read from the file.
            if not self.data:
                self.data = self.fd.read(self.BLOCK)
        # If self.data is '' then we are done.
                if not self.data:
        # Spreads DUMPED_FILE so clients of this protocol 
        # can know when their files were sent.
                    zmap(spin, WRITE, self.update)
                    spawn(spin, DUMPED_FILE)

        # We no more need to write.
        # We are done.
                    return

            size = spin.send(self.data)

    # We use buffer to send faster.
            self.data = buffer(self.data, size)

        # If it arose error when sending we deal with it.
        except socket.error as excpt:
            err = excpt.args[0]
            if err in CLOSE_ERR_CODE:
                spawn(spin, CLOSE)
            else:
                spawn(spin, SEND_ERR, excpt)
        except IOError as excpt:
            err = excpt.args[0]
            spawn(spin, READ_ERR, err)

def lose(spin):
    spin.destroy()

    try:
        spin.close()
    except Exception as excpt:
        err = excpt.args[0]
        spawn(spin, CLOSE_ERR, err)
        debug()

import sys
# Useful to print out chunks with events
# accepting this function header.
put = lambda spin, data: sys.stdout.write(data)

__all__ = ['Stdin', 'Stdout', 'Client', 'Server', 'lose', 'put', 'Read', 'Write',
            'CLOSE',
            'CONNECT',
            'LOAD', 
            'CLOSE',
            'RECV_ERR',
            'SEND_ERR',
            'ACCEPT_ERR',
            'CONNECT_ERR',
            'READ_ERR',
            'DUMPED_FILE',
            'ACCEPT',
            'DUMPED',
            'CLOSE_ERR'
          ]












