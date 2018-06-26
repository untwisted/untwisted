from untwisted.network import core

installed = False

def install_hook(obj, timeout):
    global installed

    installed = True
    core.gear.timeout = 0
    def loop():
        obj.after(timeout, loop)               
        core.gear.update()
    obj.after(timeout, loop)               

def extern(obj, timeout=200):
    """
    Tell Tkinter to process untnwisted event loop.
    It registers just once the update handle.
    """
    global installed

    # Register it just once.
    if not installed: 
        install_hook(obj, timeout)
    installed = True

def intern(obj, timeout):
    """
    Tell untwisted to process an extern event
    loop.
    """

    core.gear.timeout = timeout
    core.gear.pool.append(obj)








