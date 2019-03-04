import socket
import sys
import pickle
import json
import time


class Channel:

    def __init__(self, serialization=None):
        self.sock = None
        self.address = None
        self.serialization = serialization

    def connect(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)

    def accept(self, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(address)
        sock.listen(1)
        self.sock, self.address = sock.accept()

    def send(self, msg):
        if self.serialization == 'pickle':
            msg = pickle.dumps(msg)
        if self.serialization == 'json':
            msg = json.dumps(msg.decode('utf-8')).encode('utf-8')
        size = len(msg)
        sizemsg = size.to_bytes(4, 'big')
        self.sock.sendall(sizemsg+msg)

    def recv_exactly(self, n):
        msg = b''
        while len(msg) < n:
            new = self.sock.recv(1)
            if not new:
                raise IOError('Socket closed')
            msg += new
        return msg

    def recv(self):
        sizemsg = self.sock.recv(4)
        size = int.from_bytes(sizemsg, 'big')
        msg = self.recv_exactly(size)
        if self.serialization == 'pickle':
            msg = pickle.loads(msg)
        if self.serialization == 'json':
            msg = json.loads(msg.decode('utf-8'))
        return msg


class ReliableChannel:

    def __init__(self, serialization=None):
        self.sock = None
        self.address = None

    def connect(self, address):
        # TODO: Retry until successful
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(address)
        except:
            print(f"retrying connect({address})")
            time.sleep(1)
            self.connect(address)

    def accept(self, address):
        # TODO: Retry until successful
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(address)
        sock.listen(1)
        self.sock, self.address = sock.accept()

    def send(self, msg):
        size = len(msg)
        sizemsg = size.to_bytes(4, 'big')

        # TODO: Retry until successful
        self.sock.sendall(sizemsg)
        self.sock.sendall(msg)

    def send_raw(self, msg):
        size = len(msg)
        sizemsg = size.to_bytes(4, 'big')
        self.sock.sendall(sizemsg)
        self.sock.sendall(msg)

    def recv_exactly(self, n):
        msg = b''
        while len(msg) < n:
            # TODO: Retry until successful
            new = self.sock.recv(1)
            if not new:
                raise IOError('Socket closed')
            msg += new
        return msg

    def recv(self):
        sizemsg = self.recv_exactly(4)
        size = int.from_bytes(sizemsg, 'big')
        msg = self.recv_exactly(size)
        return msg


def client(address):
    c = Channel()
    c.connect(address)
    c.send(b'hello')

    m = c.recv()
    print(f"client received {len(m)} bytes")


def server(address, serialization=None):
    c = Channel(serialization)
    c.accept(address)

    m = c.recv()
    print(f"server received {len(m)}")

    c.send(b'good day')


def serialization_test(port):
    # you need to manually run these three respective servers ...
    # TODO: spawn processes for this so you don't need so many terminal window
    address = ('localhost', port)
    pickle_address = ('localhost', port + 1)
    json_address = ('localhost', port + 2)

    start = time.time()
    jc = Channel()
    jc.connect(address)
    jc.send(b'\x00' * 100_000)
    jc.recv()
    end = time.time()
    print(f"raw took {end - start} seconds")

    start = time.time()
    pc = Channel('pickle')
    pc.connect(pickle_address)
    pc.send(b'\x00' * 100_000)
    pc.recv()
    end = time.time()
    print(f"pickle took {end - start} seconds")

    start = time.time()
    jc = Channel('json')
    jc.connect(json_address)
    jc.send(b'\x00' * 100_000)
    jc.recv()
    end = time.time()
    print(f"json took {end - start} seconds")

def reliability_test(address):
    c = ReliableChannel()
    c.connect(address)
    print('connected')


if __name__ == '__main__':
    args = sys.argv
    command = args[1]
    port = int(args[2])
    serialization = args[3]
    address = ('localhost', port)
    if command == 'client':
        client(address)
    elif command == 'test':
        serialization_test(port)
    elif command == 'server':
        server(address, serialization)
    elif command == 'reliability-test':
        reliability_test(address)
    else:
        print('python channel.py <reliability-test|test|client|server> <address> <raw|json|pickle>')
