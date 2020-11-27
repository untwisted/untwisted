from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from queue import Queue, Empty
from untwisted.dispatcher import Dispatcher
from untwisted import core
from untwisted.event import LOAD, CLOSE
from untwisted.waker import waker

class ChildError(Exception):
    pass

class ChildThread(Dispatcher):
    SIZE = -1

    def __init__(self, child):
        self.child  = child
        self.thread = Thread(target=self.run)
        self.queue  = Queue()

        self.terminate = self.child.terminate
        core.gear.pool.append(self)

        Dispatcher.__init__(self)
        Thread.__init__(self)

        self.thread.start()

    def run(self):
        """
        """

        while True:
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
        if not data: 
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
    def __init__(self, child):
        if child.stdout is None:
            raise ChildError('Child has no stdout!')

        self.stdout = child.stdout
        super(ChildStdout, self).__init__(child)

    def read(self):
        data = self.stdout.readline(self.SIZE)
        self.queue.put_nowait(data)
        return data

class ChildStderr(ChildThread):
    def __init__(self, child):
        if child.stderr is None:
            raise ChildError('Child has no stderr!')
        self.stderr = child.stderr
        super(ChildStderr, self).__init__(child)

    def read(self):
        data = self.stderr.readline(self.SIZE)
        self.queue.put_nowait(data)
        return data

class ChildStdin:
    def __init__(self, child):
        self.child = child

        if child.stdin is None:
            raise ChildError('Child has no stdin!')

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

    def __init__(self, *args):
        """
        """

        child = Popen(args, stdout=PIPE, 
        stdin=PIPE,  stderr=STDOUT)
        self.args = args

        self.stdin = child.stdin
        self.stdout = child.stdout
        super(Expect, self).__init__(child)

