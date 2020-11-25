from untwisted.event import ACCEPT, ACCEPT_ERR, CLOSE, CONNECT, CONNECT_ERR, READ, LOAD, DUMPED, DONE
from untwisted.network import SuperSocket
from threading import Thread
from untwisted.job import Job
from untwisted.waker import waker
from untwisted.splits import Terminator
from untwisted.sock_writer import SockWriter
from untwisted.sock_reader import SockReader
from untwisted.client import Client, create_client, lose
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
        pass

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
        client.destroy()
        client.close()

        self.server.destroy()
        self.server.close()
        die()

    def test_accept(self):
        core.gear.mainloop()
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)

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
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = create_server('0.0.0.0', 1237, 5)
        self.server.add_map(ACCEPT, self.handle_accept)

        self.client = create_client('0.0.0.0', 1237)

    def handle_accept(self, server, ssock):
        self.ssock = ssock
        ssock.destroy()
        ssock.close()

        # When ssock is closed then CLOSE is spawned in self.client
        # and a handle to set down the socket is called thus there is no 
        # need to set down self.client otherwise an exception raises
        # due to multiple attempts to set down the socket.
        # self.client.destroy()
        # self.client.close()

        self.server.destroy()
        self.server.close()
        die()

    def test_accept(self):
        core.gear.mainloop()
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)
        self.assertNotIn(self.ssock, core.gear.base)

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
        if self.sent == b'abc' * 100:
            self.client.drive(DONE)

    def handle_accept(self, server, ssock):
        self.ssock = ssock
        ssock.add_map(LOAD, self.handle_load)

    def handle_done(self, ssock):
        self.client.destroy()
        self.client.close()

        self.server.destroy()
        self.server.close()
        die()

    def handle_connect(self, client):
        client.dump(b'abc' * 100)
        client.add_map(DONE, self.handle_done)

    def test_accept(self):
        core.gear.mainloop()
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)
        self.assertNotIn(self.ssock, core.gear.base)
        self.assertNotEqual(self.ssock, None)
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
        if self.sent == b'abc' * 100:
            self.ssock.drive(DONE)

    def handle_accept(self, server, ssock):
        self.ssock = ssock

        ssock.dump(b'abc' * 100)
        ssock.add_map(DONE, self.handle_done)

    def handle_done(self, ssock):
        ssock.destroy()
        ssock.close()

        self.server.destroy()
        self.server.close()
        die()

    def test_accept(self):
        core.gear.mainloop()
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)
        self.assertNotEqual(self.ssock, None)
        self.assertNotIn(self.ssock, core.gear.base)
        self.assertEqual(self.sent, b'abc' * 100)

class TestSockAccUntil(unittest.TestCase):
    pass

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
            self.ssock.drive(DONE)

    def handle_accept(self, server, ssock):
        self.ssock = ssock

        ssock.dump(b'abc\r\n' * 100)
        ssock.add_map(DONE, self.handle_done)

    def handle_connect(self, client):
        Terminator(client)
        client.add_map(Terminator.FOUND, self.handle_found)

    def handle_done(self, ssock):
        ssock.destroy()
        ssock.close()

        self.server.destroy()
        self.server.close()
        die()

    def test_accept(self):
        core.gear.mainloop()
        self.assertNotIn(self.server, core.gear.base)
        self.assertNotIn(self.client, core.gear.base)
        self.assertNotEqual(self.ssock, None)
        self.assertNotIn(self.ssock, core.gear.base)
        self.assertEqual(self.sent, b'abc' * 100)

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