from untwisted.timer import Sched
from untwisted import core

def callback():
    print('Executed!')

if __name__ == '__main__':
    timer = Sched(2, callback) 
    core.gear.mainloop()
