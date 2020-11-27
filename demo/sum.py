from untwisted import core
from untwisted.job import Job, DONE
import time

def sum(x, y):
    time.sleep(3)
    return x + y

def show(job, result):
    print(result)

for ind in range(100):
    job = Job(sum, ind, 1000)
    job.add_map(DONE, show)

core.gear.mainloop()




