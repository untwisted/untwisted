from untwisted.event import ACCEPT, ACCEPT_ERR, CLOSE, CONNECT, CONNECT_ERR, READ, LOAD, DUMPED, DONE
from untwisted.network import SuperSocket
from threading import Thread
from untwisted.job import Job
from untwisted.waker import waker
from untwisted.splits import Terminator, AccUntil
from untwisted.sock_writer import SockWriter
from untwisted.sock_reader import SockReader
from untwisted.client import Client, create_client, lose
from untwisted.dispatcher import Dispatcher, Stop, Erase
from untwisted.server import create_server
from untwisted.core import die
from untwisted import core
import unittest
import time

class TestExpect(unittest.TestCase):
    def setUp(self):
        pass

class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.add_map('event0', self.handle_event0, False, True)
        self.dispatcher.add_map('event1', self.handle_event1, False)
        self.dispatcher.add_map('event2', self.handle_event2, False)
        self.dispatcher.add_map('event3', self.handle_event3, False)
        self.dispatcher.add_map('event4', self.handle_event4)

    def handle_event0(self, dispatcher, value0, value1):
        self.assertEqual(value1, True)
        self.assertEqual(value0, False)

    def handle_event1(self, dispatcher, value0, value1, value2):
        self.assertEqual(value2, False)
        self.assertEqual(value1, True)
        self.assertEqual(value0, True)

    def handle_event2(self, dispatcher, value0, value1):
        self.assertEqual(value1, False)
        self.assertEqual(value0, True)

    def handle_event3(self, dispatcher, value):
        self.assertEqual(value, False)

    def handle_event4(self, dispatcher):
        raise Stop

    def test_dispatcher(self):
        self.dispatcher.drive('event0')
        self.dispatcher.drive('event1', True, True)
        self.dispatcher.drive('event2', True)
        self.dispatcher.drive('event3')
        self.dispatcher.drive('event4')

class TestJob(unittest.TestCase):
    def setUp(self):
        job = Job(self.do_job)
        job.add_map(DONE, self.handle_done)
        self.retval = False

    def handle_done(self, job, retval):
        self.retval = retval
        die()

    def do_job(self):
        time.sleep(1)
        return True

    def test_job(self):
        core.gear.mainloop()
        self.assertEqual(self.retval, True)

class TestTask(unittest.TestCase):
    def setUp(self):
        pass

class TestClient(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1236, 5)

        self.client = create_client('0.0.0.0', 1236)
        self.client.add_map(CONNECT, self.handle_connect)

    def handle_connect(self, client):
        print('Connected!', client)
        lose(client)
        lose(self.server)
        die()

    def test_accept(self):
        core.gear.mainloop()

class TestLose(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1235, 5)

        self.client = SuperSocket()
        self.client.connect_ex(('0.0.0.0', 1235))

        Client(self.client)
        self.client.add_map(CONNECT, self.handle_connect)

    def handle_connect(self, client):
        lose(client)
        lose(self.server)
        die()

    def test_accept(self):
        core.gear.mainloop()

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1237, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1237)

    def handle_accept(self, server, ssock):
        print('Accepted:', ssock)
        lose(ssock)
        lose(self.server)
        die()

    def test_accept(self):
        core.gear.mainloop()

class TestSockWriter(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1238, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1238)
        self.client.add_map(CONNECT, self.handle_connect)
        self.sent = b''
        self.ssock = None

    def handle_load(self, ssock, data):
        self.sent = self.sent + data

    def handle_accept(self, server, ssock):
        self.ssock = ssock
        ssock.add_map(LOAD, self.handle_load)

    def handle_done(self, ssock, data):
        print('Received bytes from:', ssock)
        lose(ssock)
        lose(self.server)
        die()

    def handle_connect(self, client):
        client.dump(b'abc' * 100)
        client.add_map(DUMPED, self.handle_dumped)

    def handle_dumped(self, client):
        print('Sent from:', client)
        self.ssock.add_map(LOAD, self.handle_done)

    def test_accept(self):
        core.gear.mainloop()
        self.assertEqual(self.sent, b'abc' * 100)

class TestSockReader(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1239, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1239)
        self.client.add_map(LOAD, self.handle_load)
        self.sent = b''
        self.ssock = None

    def handle_load(self, client, data):
        self.sent = self.sent + data

    def handle_accept(self, server, ssock):
        self.ssock = ssock

        ssock.dump(b'abc' * 100)
        ssock.add_map(DUMPED, self.handle_dumped)

    def handle_dumped(self, ssock):
        print('Sent from:', ssock)
        self.client.add_map(LOAD, self.handle_done)

    def handle_done(self, client, data):
        print('Received bytes from:', self.client)
        lose(client)
        lose(self.server)
        die()

    def test_accept(self):
        core.gear.mainloop()

class TestSockAccUntil(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1241, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1241)
        self.client.add_map(CONNECT, self.handle_connect)

    def handle_done(self, client, a, b):
        self.assertEqual(a, b'abc' * 100)
        self.assertEqual(b, b'efg' * 100)
        lose(client)
        lose(self.server)
        die()

    def handle_accept(self, server, ssock):
        ssock.dump(b'abc' * 100 + b'\r\n\r\n' + b'efg'* 100)

    def handle_connect(self, client):
        acc = AccUntil(client)
        acc.start()
        client.add_map(AccUntil.DONE, self.handle_done)

    def test_accept(self):
        core.gear.mainloop()

class TestTerminator(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1240, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1240)
        self.client.add_map(CONNECT, self.handle_connect)

        self.sent  = b''
        self.ssock = None

    def handle_found(self, client, data):
        self.sent = self.sent + data
        if self.sent == b'abc' * 100:
            self.terminate()

    def terminate(self):
        lose(self.ssock)
        lose(self.server)
        die()

    def handle_accept(self, server, ssock):
        self.ssock = ssock
        ssock.dump(b'abc\r\n' * 100)

    def handle_connect(self, client):
        Terminator(client)
        client.add_map(Terminator.FOUND, self.handle_found)

    def test_accept(self):
        core.gear.mainloop()

class TestTmpFile(unittest.TestCase):
    def setUp(self):
        pass

class HandleWakeup:
    def update(self):
        die()

class TestWaker(unittest.TestCase):
    def setUp(self):
        self.handlewakeup = HandleWakeup()
        core.gear.pool.append(self.handlewakeup)
        thread = Thread(target=self.do_job)
        thread.start()

    def do_job(self):
        time.sleep(1)
        waker.wake_up()

    def test_wakeup(self):
        core.gear.mainloop()
        # Remove the object off the pool otherwise it will
        # just break the mainloop in the other test cases.
        core.gear.pool.remove(self.handlewakeup)

class TestFileReader(unittest.TestCase):
    def setUp(self):
        pass

class TestFileWriter(unittest.TestCase):
    def setUp(self):
        pass

class TestTimer(unittest.TestCase):
    def setUp(self):
        pass

class TestSched(unittest.TestCase):
    def setUp(self):
        pass

class TestClientSSL(unittest.TestCase):
    def setUp(self):
        pass

class TestSockWriterSSL(unittest.TestCase):
    def setUp(self):
        pass

class TestSockReaderSSL(unittest.TestCase):
    def setUp(self):
        pass

class TestSockReaderSSL(unittest.TestCase):
    def setUp(self):
        pass

class TestSuperSocket(unittest.TestCase):
    def setUp(self):
        pass

class TestDevice(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()