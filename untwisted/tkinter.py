from untwisted.network import core

def extern(obj, timeout=200):
    core.gear.timeout = 0

    def loop():
        obj.after(timeout, loop)               
        core.gear.update()
    
    obj.after(timeout, loop)               

def intern(obj, timeout):
    core.gear.timeout = timeout
    core.gear.pool.append(obj)







