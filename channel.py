import socket
import pickle
import json
import time


class Channel:

    def __init__(self, serialization=None):
        self.sock = None
        self.connection = None
        self.server_address = None
        self.client_address = None
        self.serialization = serialization

    def connect(self, address):
        self.server_address = address
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect(address)
        except:
            print(f"retrying connect({address})")
            time.sleep(1)
            self.connect(address)

    def accept(self, address):
        self.server_address = address
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(address)
            self.sock.listen(1)
        self.connection, self.client_address = self.sock.accept()

    def reconnect(self):
        self.accept(self.server_address)

    def send(self, msg):
        if self.serialization == 'pickle':
            msg = pickle.dumps(msg)
        if self.serialization == 'json':
            msg = json.dumps(msg.decode('utf-8')).encode('utf-8')
        size = len(msg)
        sizemsg = size.to_bytes(4, 'big')
        self.connection.sendall(sizemsg+msg)

    def recv_exactly(self, n):
        msg = b''
        while len(msg) < n:
            new = self.connection.recv(1)
            if not new:
                raise IOError('Socket closed')
            msg += new
        return msg

    def recv(self):
        sizemsg = self.recv_exactly(4)
        size = int.from_bytes(sizemsg, 'big')
        msg = self.recv_exactly(size)
        if self.serialization == 'pickle':
            msg = pickle.loads(msg)
        if self.serialization == 'json':
            msg = json.loads(msg.decode('utf-8'))
        return msg
