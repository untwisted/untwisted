from untwisted.timer import Timer
from untwisted import core

def callback():
    print('Executed!')

if __name__ == '__main__':
    timer = Timer(2, callback) 
    core.gear.mainloop()