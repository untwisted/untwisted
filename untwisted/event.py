"""
Built-in events.
"""

class Event:
    pass

class READ(Event):
    pass

class WRITE(Event):
    pass

class ERROR(Event):
    pass

class DESTROY(Event):
    pass

class CLOSE(Event):
    pass

class ACCEPT(Event):
    pass

class CONNECT(Event):
    pass

class CONNECT_ERR(Event):
    pass

class LOAD(Event):
    pass

class DUMPED(Event):
    pass

class RECV_ERR(Event):
    pass

class SEND_ERR(Event):
    pass

class ACCEPT_ERR(Event):
    pass

class READ_ERR(Event):
    pass

class DUMPED_FILE(Event):
    pass

class CLOSE_ERR(Event):
    pass

class DONE(Event):
    pass

class TIMEOUT(Event):
    pass

class SSL_SEND_ERR(Event):
    pass

class SSL_RECV_ERR(Event):        
    pass

class SSL_CERTIFICATE_ERR(Event): 
    pass

class SSL_CONNECT_ERR(Event):     
    pass

class SSL_CONNECT(Event):         
    pass

