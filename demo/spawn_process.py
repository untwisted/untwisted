from untwisted.expect import ChildStdout, ChildStderr, ChildStdin
from subprocess import Popen, PIPE
from untwisted.event import LOAD, CLOSE
from untwisted.core import die
from untwisted import core


def on_stdout(stdout, data):
    print('Stdout data: ', data)

def on_stderr(stderr, data):
    print('Stderr data:', data)

def on_close(expect):
    print('Closing..')
    die()

if __name__ == '__main__':
    code = b'print("hello world")\nprint(1/0)\nquit()\n'

    proc   = Popen(['python', '-i', '-u'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdin  = ChildStdin(proc)
    stdout = ChildStdout(proc)
    stderr = ChildStderr(proc)
    
    stdin.send(code)
    stdout.add_map(LOAD, on_stdout)
    stderr.add_map(LOAD, on_stderr)
    stdout.add_map(CLOSE, on_close)
    core.gear.mainloop()
    