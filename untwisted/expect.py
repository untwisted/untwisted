from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from queue import Queue
from untwisted.dispatcher import Dispatcher
from untwisted import core
from untwisted.event import LOAD, CLOSE
from untwisted.waker import waker
import shlex
import os

class ChildError(Exception):
    pass

class ChildThread(Dispatcher):
    SIZE = -1

    def __init__(self, child):
        self.child  = child
        self.thread = Thread(target=self.run)
        self.queue  = Queue()

        core.gear.pool.append(self)
        self.done = False

        Dispatcher.__init__(self)

        Thread.__init__(self)

        self.thread.start()

    def terminate(self):
        self.done = True
        self.child.terminate()

        self.child.stdin.close()
        self.child.stdout.close()

    def run(self):
        """
        """

        while not self.done:
            data = self.read()
            waker.wake_up()
            if not data: 
                break
        self.child.wait()

    def update(self):
        """
        """
        while not self.queue.empty():
            self.dispatch()

    def dispatch(self):
        data = self.queue.get_nowait()
        if (not data) or self.done: 
            self.drive(CLOSE)
        else: 
            self.drive(LOAD, data)

    def destroy(self):
        """
        Unregister up from untwisted reactor. It is needed
        to call self.terminate() first to kill the process.
        """
        core.gear.pool.remove(self)    
        self.base.clear()

class ChildStdout(ChildThread):
    """
    An event emitter to read data from a process stdout stream.
    """

    def __init__(self, child):
        super(ChildStdout, self).__init__(child)

    def read(self):
        data = self.child.stdout.readline(self.SIZE)
        self.queue.put_nowait(data)
        return data

class ChildStderr(ChildThread):
    """
    An event emitter to read data from a process stderr stream.
    """

    def __init__(self, child):
        super(ChildStderr, self).__init__(child)

    def read(self):
        data = self.child.stderr.readline(self.SIZE)
        self.queue.put_nowait(data)
        return data

class ChildStdin:
    """
    A wrapper around a process stdin stream to dump data to an
    underlying process.
    """

    def __init__(self, child):
        self.child = child

    def send(self, data):
        """
        Send data to the child process through.
        """
        self.child.stdin.write(data)
        self.child.stdin.flush()

class Expect(ChildStdout, ChildStdin):
    """
    This class is used to spawn processes.

    python = Expect('python2.7', '-i')
    python.send('print "hello world"')
    python.terminate()
    python.destroy()
    """

    def __init__(self, cmd, *args, **kwargs):
        """
        
        """    
        child = Popen(shlex.split(cmd), *args, stdout=PIPE, 
        stdin=PIPE, stderr=STDOUT, **kwargs)

        super(Expect, self).__init__(child)

