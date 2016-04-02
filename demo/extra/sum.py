from untwisted.network import core
from untwisted.job import Job
import time

def sum(x, y):
    time.sleep(3)
    return x + y

def show(result):
    print result

for ind in xrange(100):
    job = Job(show, sum, ind, 1000)

core.gear.mainloop()


