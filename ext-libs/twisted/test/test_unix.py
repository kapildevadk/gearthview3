import os
import socket
import stat
import sys
import pytest
import twisted.internet
import twisted.internet.interfaces
import twisted.internet.protocol
import twisted.internet.error
import twisted.internet.address
import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.utils
import twisted.python.lockfile
import twisted.trial.unittest
from twisted.test.test_tcp import MyServerFactory, MyClientFactory


@pytest.fixture
def temp_filename():
    return tempfile.NamedTemporaryFile(mode="w", delete=False).name


@pytest.fixture
def temp_peername(temp_filename):
    return tempfile.NamedTemporaryFile(mode="w", delete=False).name


@pytest.mark.skipif(
    not twisted.internet.interfaces.IReactorUNIX(twisted.internet.reactor, None),
    reason="This reactor does not support UNIX domain sockets",
)
class TestUnixSocket(twisted.trial.unittest.TestCase):
    def test_peer_bind(self, temp_filename, temp_peername):
        server_factory = MyServerFactory()
        conn_made = server_factory.protocolConnectionMade = twisted.internet.defer.Deferred()
        unix_port = twisted.internet.reactor.listenUNIX(
            temp_filename, server_factory
        )

        def stop_listening():
            unix_port.stopListening()
            os.remove(temp_filename)
            os.remove(temp_peername.name)

        self.addCleanup(stop_listening)

        unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        unix_socket.bind(temp_peername.name)
        unix_socket.connect(temp_filename)

        def cb_conn_made(proto):
            expected = twisted.internet.address.UNIXAddress(temp_peername.name)
            self.assertEqual(server_factory.peerAddresses, [expected])
            self.assertEqual(proto.transport.getPeer(), expected)

        conn_made.addCallback(cb_conn_made)
        return conn_made

    def test_dumber(self, temp_filename):
        server_factory = MyServerFactory()
        server_conn_made = twisted.internet.defer.Deferred()
        server_factory.protocolConnectionMade = server_conn_made
        unix_port = twisted.internet.reactor.listenUNIX(temp_filename, server_factory)

        def stop_listening():
            unix_port.stopListening()
            os.remove(temp_filename)

        self.addCleanup(stop_listening)

        client_factory = MyClientFactory()
        client_conn_made = twisted.internet.defer.Deferred()
        client_factory.protocolConnectionMade = client_conn_made

        twisted.internet.reactor.connectUNIX(
            temp_filename, client_factory
        )

        d = twisted.internet.defer.gatherResults([server_conn_made, client_conn_made])

        def all_connected((server_protocol, client_protocol)):
            self.assertEqual(
                client_factory.peerAddresses,
                [twisted.internet.address.UNIXAddress(temp_filename)],
            )

            client_protocol.transport.loseConnection()
            server_protocol.transport.loseConnection()

        d.addCallback(all_connected)
        return d


@pytest.mark.skipif(
    not twisted.internet.interfaces.IReactorUNIX(twisted.internet.reactor, None),
    reason="This reactor does not support UNIX domain sockets",
)
class TestUnixSocketLocking(twisted.trial.unittest.TestCase):
    def test_socket_locking(self, temp_filename):
        server_factory = MyServerFactory()
        unix_port = twisted.internet.reactor.listenUNIX(
            temp_filename, server_factory, wantPID=True
        )

        self.assertRaises(
            twisted.internet.error.CannotListenError,
            twisted.internet.reactor.listenUNIX,
            temp_filename,
            server_factory,
            wantPID=True,
        )

        def stop_listening():
            unix_port.stopListening()
            os.remove(temp_filename)

        self.addCleanup(stop_listening)


@pytest.mark.skipif(
    not twisted.internet.interfaces.IReactorUNIX(twisted.internet.reactor, None),
    reason="This reactor does not support UNIX domain sockets",
)
class TestUnixSocketPIDFile(twisted.trial.unittest.TestCase):
    def test_pid_file(self, temp_filename):
        server_factory = MyServerFactory()
        server_conn_made = twisted.internet.defer.Deferred()
        server_factory.protocolConnectionMade = server_conn_made
        unix_port = twisted.internet.reactor.listenUNIX(
            temp_filename, server_factory, wantPID=True
        )

        def stop_listening():
            unix_port.stopListening()
            os.remove(temp_filename)

        self.addCleanup(stop_listening)

        self.assertTrue(
            twisted.python.lockfile.isLocked(f"{temp_filename}.lock")
        )

        client_factory = MyClientFactory()
        client_conn_made = twisted.internet.defer
