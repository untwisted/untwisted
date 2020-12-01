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

class READ_ERR(Event):
    pass

class DUMPED_FILE(Event):
    pass

class DONE(Event):
    pass

class TIMEOUT(Event):
    pass

class SSL_CONNECT_ERR(Event):     
    pass

class SSL_CONNECT(Event):         
    pass

class SSL_ACCEPT(Event):         
    pass

class SSL_ACCEPT_ERR(Event):
    pass
