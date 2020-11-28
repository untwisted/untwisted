from untwisted.core import die
from untwisted import core
from untwisted.task import Task
from untwisted.job import Job, DONE
import time

def sum(x, y):
    time.sleep(3)
    return x + y

def show(job, result):
    print(result)

task = Task()
# Tell the task it can start trigging events.
task.start()

for ind in range(100):
    job = Job(sum, ind, 1000)
    job.add_map(DONE, show)
    task.add(job, DONE)

task.add_map(DONE, lambda task: die())
core.gear.mainloop()




