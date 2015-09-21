""" 
"""

from untwisted.utils.shrug import FOUND
from untwisted.tools import ip_to_long, long_to_ip
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.fixed import *
from untwisted.task import sched
from struct import pack, unpack
from textwrap import wrap
from socket import *
import re
import sys

TIMEOUT        = get_event()
DONE           = get_event()
RFC_STR        = "^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<arguments> .+))?"
RFC_REG        = re.compile(RFC_STR)
PREFIX_STR     = "(?P<nick>.+)!(?P<user>.+)@(?P<host>.+)"
PREFIX_REG     = re.compile(PREFIX_STR)
PRIVMSG_HEADER = 'PRIVMSG %s :%s\r\n'
CMD_HEADER = '%s\r\n'


class DccServer(Spin):
    """ 
    This class is used to send files. It is called DccServer cause the one sending 
    a file is the one who sets up a server.
    """

    def __init__(self, file_obj, port, timeout=20):
        """ 
        Class constructor.
        file_obj -> The file that is being sent.
        port     -> The port which will be used.
        timeout  -> How long the server must be up.
        """

        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('', port))
        sock.listen(1)

        Spin.__init__(self, sock)
        self.file_obj = file_obj
        self.timeout = timeout
        self.port = port
       
        Server(self)

        self.is_on = False
        xmap(self, ACCEPT, self.start_transfer) 

        sched.after(self.timeout, self.run_timeout, True)
        
    def run_timeout(self):
        """
        """

        if not self.is_on:
            spawn(self, TIMEOUT)
        lose(self)

    def start_transfer(self, server, client):
        """
        """

        xmap(client, WRITE, self.send_file) 
        Stdout(client)
        Stdin(client)

        Fixed(client)

        xmap(client, CLOSE, lambda con, err: lose(con)) 
        xmap(client, BOX, self.run_done) 

        self.is_on = True
        hook(self, client, CLOSE, DONE)

    def send_file(self, client):
        """
        """

        data = self.file_obj.read(1024)
        if not data:
           zmap(client, WRITE, self.send_file) 
           #xmap(client, DUMPED, self.run_done)
        else:
            client.dump(data)

    def run_done(self, client, chunk):
        """
        """

        pos = unpack("!I", chunk)[0]

        if not pos >= self.file_obj.tell(): 
            return

        spawn(client, DONE)
        lose(client)


class DccClient(Spin):
    def __init__(self, host, port, file_obj, size):
        """
        """

        sock = socket(AF_INET, SOCK_STREAM)

        Spin.__init__(self, sock)

        self.port = port
        self.file_obj = file_obj
        self.size = size
        
        Client(self)
        self.connect_ex((host, port))
        
   
        xmap(self, CONNECT, self.set_up_con) 
        xmap(self, CONNECT_ERR, lambda con, err: lose(con)) 

    def set_up_con(self, client):
        """
        """

        Stdout(self)
        Stdin(self)
        xmap(self, LOAD, self.recv_file) 
        xmap(self, CLOSE, lambda con, err: lose(con)) 
 

    def recv_file(self, client, data):
        """
        """

        self.file_obj.write(data)

        # It packs the ack.
        ack = pack('!I', self.file_obj.tell())

        # it sends the ack.
        client.dump(ack)

        if not self.file_obj.tell() >= self.size:
            return

        zmap(self, LOAD, self.recv_file) 

        yield hold(self, DUMPED)

        spawn(client, DONE)
        lose(client)

class Irc(object):
    def __init__(self, spin):
        """ 
        Install the protocol inside a Spin instance. 
        """

        xmap(spin, FOUND, self.main)
    
    def main(self, spin, data):
        """ 
        The function which uses irc rfc regex to extract
        the basic arguments from the msg.
        """

        field = re.match(RFC_REG, data)
        
        if not field:
            return
    
        prefix  = self.extract_prefix(field.group('prefix'))
        command = field.group('command').upper()
        args    = self.extract_args(field.group('arguments'))
        spawn(spin, command, *(prefix + args))
    
    def extract_prefix(self, prefix):
        """ 
        It extracts an irc msg prefix chunk 
        """

        field = re.match(PREFIX_REG, prefix if prefix else '')
        
        return (prefix,) if not field else field.group(1, 2, 3)
    
    def extract_args(self, data):
        """ 
        It extracts irc msg arguments. 
        """
    
        args = []
        try:
            lhs, rhs = self.fmt_args(data)
        except ValueError:
            args.extend(data.split(' '))
        else:
            if lhs: 
                args.extend(lhs.split(' '))
            args.append(rhs)
        return tuple(args)
    
    def fmt_args(self, data):
        data     = data.strip(' ')
        lhs, rhs = data.split(':', 1)
        lhs      = lhs.rstrip(' ')
        return lhs, rhs

class CTCP(object):
    def __init__(self, spin):
        """ 
        It installs the subprotocol inside a Spin
        instance.
        """
        xmap(spin, 'PRIVMSG', self.extract_ctcp)
    
        xmap(spin, 'DCC', self.patch)
    
    def extract_ctcp(self, spin, nick, user, host, target, msg):
        """ 
        it is used to extract ctcp requests into pieces.
        """
    
        # The ctcp delimiter token.
        DELIM = '\001'
    
        if not msg.startswith(DELIM) or not msg.endswith(DELIM):
            return
    
        ctcp_args = msg.strip(DELIM).split(' ') 
        
        spawn(spin, ctcp_args[0], (nick, user, host,  target, msg), *ctcp_args[1:])
    
    def patch(self, spin, header, *args):
        """ 
        It spawns DCC TYPE as event. 
        """

        spawn(spin, 'DCC %s' % args[0], header, *args[1:])
    

def send_msg(server, target, msg):
    list_chunk = wrap(msg, width=512)

    for ind in list_chunk:
        server.dump(PRIVMSG_HEADER % (target, ind))

def send_cmd(server, cmd):
    server.dump(CMD_HEADER % cmd)





