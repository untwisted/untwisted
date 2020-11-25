from untwisted.network import SuperSocket
# Builtin handle/extension to spawn CONNECT, CONNECT_ERR events.
from untwisted.client import Client
# Builtin events.
from untwisted.event import CONNECT, CONNECT_ERR
from untwisted import core

def handle_connect(ssock):
    print('Connected !')

def handle_connect_err(ssock, err):
    print('Not connected:', err)

ssock = SuperSocket()
Client(ssock)
ssock.connect_ex(('httpbin.org', 80))

# Map handles to the events from Client handle.
ssock.add_map(CONNECT, handle_connect)
ssock.add_map(CONNECT_ERR, handle_connect_err)

# Start reactor to scale socket READ/WRITE events asynchronously.
core.gear.mainloop()

