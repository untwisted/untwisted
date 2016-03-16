# Whenever we use get_event it increases
# So we don't get events messed.
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







