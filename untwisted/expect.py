from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from Queue import Queue, Empty
from os import environ, setsid, killpg
from untwisted.mode import Mode
from untwisted.core import get_event
from untwisted import core
from untwisted.utils.stdio import LOAD, CLOSE

class Expect(Thread, Mode):
    SIZE = 1024 * 124

    def __init__(self, *args):
        """
        """

        self.child = Popen(args, shell=0, stdout=PIPE, stdin=PIPE,  
                                            stderr=STDOUT,  env=environ)
        self.stdin  = self.child.stdin
        self.stdout = self.child.stdout
        self.stderr = self.child.stderr
        self.args  = args
        self.queue = Queue()
        self.stop  = False

        core.gear.pool.append(self)

        Mode.__init__(self)
        Thread.__init__(self)

        self.start()

    def send(self, data):
        """
        """

        data = data.encode('utf-8')
        self.stdin.write(data)

    def run(self):
        """
        """

        while not self.stop:
            if not self.feed(): break
            core.gear.wake()
        self.child.wait()

    def feed(self):
        try:
            data = self.stdout.readline()
        except Exception as e:
            self.queue.put_nowait('')
        else:
            self.queue.put_nowait(data)
        finally:
            return data

    def update(self):
        """
        """
        while not self.queue.empty():
            self.dispatch()

    def dispatch(self):
        data = self.queue.get_nowait()
        if not data: 
            self.drive(CLOSE)
        else: 
            self.drive(LOAD, data)


    def destroy(self):
        """
        """
        self.stop = True
        self.child.kill()
        core.gear.pool.remove(self)    






