from untwisted.job import Job, DONE
from untwisted import core
from untwisted.usual import xmap
import time

def sum(x, y):
    time.sleep(3)
    return x + y

def show(job, result):
    print result

for ind in xrange(100):
    job = Job(sum, ind, 1000)
    xmap(job, DONE, show)

core.gear.mainloop()



