################################################################################

import socket
import select
import config

################################################################################

def debug(source, text):
    if config.DEBUG:
        print source, text

################################################################################

class Connection:
    buffer_in = ''
    buffer_out = ''

    def __init__(self, server, socket_accept):
        self.server = server
        self.socket, self.addr = socket_accept
        self.connected = True
        debug(self, "CONNECTED")
        self.socket_setmode('r')

    def __repr__(self):
        if self.socket:
            fileno = self.socket.fileno()
        else:
            fileno = -1
        return "<Connection fileno='%i' addr='%s' buffer_in='%i' buffer_out='%i'>" % (
            fileno, self.addr, len(self.buffer_in), len(self.buffer_out))

    def socket_setmode(self, mode):
        """Configure which events we want to get"""
        debug(self, "SETMODE %s" % mode)
        self.server.socket_setmode(self.socket, mode, self)

    def disconnect(self):
        """Disconnect the current connection"""
        debug(self, "DISCONNECT")
        if self.connected:
            self.socket_setmode(None)
            try:
                self.socket.close()
            except IOError:
                pass
        self.connected = False
        self.socket = None

    def connect(self):
        """Establish the connection"""
        assert(self.connected == False)
        debug(self, "CONNECT")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(self.addr)
        except socket.error:
            debug(self, "CONNECT FAILED")
            self.disconnect()
            return

        self.connected = True
        self.socket_setmode('r')

    def event(self, event):
        # EPOLLIN events goes to the net_receive function
        if event & select.EPOLLIN:
            self.net_receive()
        # EPOLLOUT events goes to the net_send function
        if event & select.EPOLLOUT:
            self.net_send()

    def net_receive(self):
        # If there is data to from the network, read up to 4096 bytes of it
        try:
            data = self.socket.recv(4096)
        except socket.error:
            data = None

        # If there is no data, it means we got disconnected
        if not data:
            self.disconnect()
            return

        # Strip \r
        data = data.replace('\r', '')

        # Add the data to our input buffer
        debug(self, "<<< %s" % data)
        self.buffer_in += data

        if len(self.buffer_in) > 4096:
            self.disconnect()
            return

        lines = self.parse_buffer()
        for line in lines:
            self.server.process_line(self, line)

    def net_send(self):
        # If there is data in the out buffer, send 4096 bytes of it
        data = self.buffer_out[:4096]
        self.buffer_out = self.buffer_out[4096:]
        if data:
            debug(self, ">>> %s" % data)
            self.socket.send(data)

        # If there is no more data to send, we only want to be informed of read events
        if not self.buffer_out:
            self.socket_setmode('r')

    def send(self, data):
        self.buffer_out += data
        if not self.connected:
            self.connect()
        self.socket_setmode('rw')

    def parse_buffer(self):
        lines = self.buffer_in.split('\n')
        if len(lines) == 1:
            return []
        self.buffer_in = lines[-1]
        return lines[:-1]

class Server:
    name = "TCPServer"
    epoll = select.epoll()
    sockets = {}

    def __init__(self, traderbot, config):
        # Create a Server Socket for incoming connections
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', config['LISTEN_PORT']))
        self.socket.listen(1)
        self.socket.setblocking(0)

        # Register our socket
        self.socket_setmode(self.socket, 'r', self)

    def socket_setmode(self, socket, mode, callback_obj):
        if not socket:
            return
        if not mode:
            del self.sockets[socket.fileno()]
            self.epoll.unregister(socket.fileno())
            return

        modes = {
            'r': select.EPOLLIN,
            'rw': select.EPOLLIN + select.EPOLLOUT,
        }

        if not self.sockets.has_key(socket.fileno()):
            self.sockets[socket.fileno()] = callback_obj
            self.epoll.register(socket.fileno(), modes[mode])
        else:
            self.sockets[socket.fileno()] = callback_obj
            self.epoll.modify(socket.fileno(), modes[mode])

    def run(self, timeout=5):
        try:
            events = self.epoll.poll(timeout)
        except IOError:
            # IOError: [Errno 4] Interrupted system call
            return

        for fileno, event in events:
            assert(self.sockets.has_key(fileno) == True)
            self.sockets[fileno].event(event)

    def clients_cleanup(self):
        for client in list(self.clients):
            if client.retired():
                debug(self, "RETIRED %s" % client)
                # Remove the client from our client list
                del self.clients[client]
                del client

    def event(self, event):
        assert(event == 1)
        connection = Connection(self, self.socket.accept())

    def register_callback(self, callback):
        self.callback = callback

    def process_line(self, connection, line):
        connection.send(self.callback(line))
