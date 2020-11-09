"""
Built-in events.
"""

event_count = 0

def get_event():
    """ 
    It returns a new event signal.

    from untwisted.network import *
    X = get_event()
    Y = get_event()
    print X
    print Y


    Whenever we call get_event it increases the integer
    corresponding to the signal. That avoids events getting
    messed through modules.
    """

    global event_count

    event_count = event_count + 1
    return event_count

READ             = get_event()
WRITE            = get_event()
EXPT             = get_event()
ERROR            = get_event()
DESTROY          = get_event()
LOST             = get_event()
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
DONE             = get_event()
TIMEOUT          = get_event()
SSL_SEND_ERR        = get_event()
SSL_RECV_ERR        = get_event()
SSL_CERTIFICATE_ERR = get_event()
SSL_CONNECT_ERR     = get_event()
SSL_CONNECT         = get_event()

CODE = {
READ: 'READ', 
WRITE: 'WRITE', 
EXPT: 'EXPT', 
ERROR: 'ERROR', 
DESTROY: 'DESTROY', 
LOST: 'LOST', 
CLOSE: 'CLOSE', 
ACCEPT: 'ACCEPT', 
CONNECT: 'CONNECT', 
CONNECT_ERR: 'CONNECT_ERR', 
LOAD: 'LOAD', 
DUMPED: 'DUMPED', 
RECV_ERR: 'RECV_ERR', 
SEND_ERR: 'SEND_ERR', 
ACCEPT_ERR: 'ACCEPT_ERR', 
READ_ERR: 'READ_ERR', 
DUMPED_FILE: 'DUMPED_FILE', 
CLOSE_ERR: 'CLOSE_ERR', 
DONE: 'DONE', 
TIMEOUT: 'TIMEOUT', 
SSL_SEND_ERR: 'SSL_SEND_ERR', 
SSL_RECV_ERR: 'SSL_RECV_ERR', 
SSL_CERTIFICATE_ERR: 'SSL_CERTIFICATE_ERR', 
SSL_CONNECT_ERR: 'SSL_CONNECT_ERR', 
SSL_CONNECT: 'SSL_CONNECT', 
}

