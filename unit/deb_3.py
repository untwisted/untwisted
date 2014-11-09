from untwisted.network import *
from untwisted.task import *

def call(data, number):
    print(data, number)


sched.mark(2, call, 'tau', number=32)
core.gear.mainloop()
