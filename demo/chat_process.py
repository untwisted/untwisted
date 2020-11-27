from untwisted.network import Device
from untwisted.file_reader import FileReader, LOAD, CLOSE
from untwisted.file_writer import FileWriter, DUMPED
from untwisted.client import lose
from subprocess import Popen, PIPE, STDOUT
from untwisted import core
from untwisted.core import Kill

def on_close(dev, err):
    print('On CLOSE ...', err)
    lose(dev)
    raise Kill

def on_load(dev, data):
    print('On LOAD ...', data)

child   = Popen(['python3', '-i'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)

stdout  = Device(child.stdout)
stdin   = Device(child.stdin)

FileWriter(stdin)
FileReader(stdout)

stdin.dump(b'print "hello world!"\n')
stdin.add_map(DUMPED, lambda dev: stdin.dump(b'quit()\n'))
stdout.add_map(LOAD, on_load)
stdin.add_map(CLOSE, on_close)
stdout.add_map(CLOSE, on_close)

core.gear.mainloop()





