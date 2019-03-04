import socket
import sys


class Channel:

    def __init__(self):
        self.sock = None
        self.address = None

    def connect(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)

    def accept(self, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(address)
        sock.listen(1)
        self.sock, self.address = sock.accept()

    def send(self, msg):
        size = len(msg)
        sizemsg = size.to_bytes(4, 'big')
        self.sock.sendall(sizemsg + msg)

    def recv(self):
        msg = b''
        sizemsg = self.sock.recv(4)
        assert len(sizemsg) == 4
        size = int.from_bytes(sizemsg, 'big')
        while len(msg) < size:
            msg += self.sock.recv(1)
        return msg


def client(address):
    c = Channel()
    c.connect(address)
    c.send(b'hello from client')

    m = c.recv()
    print("client received:", m)


def server(address):
    c = Channel()
    c.accept(address)

    m = c.recv()
    print("server received:", m)

    c.send(b'good day from server')


if __name__ == '__main__':
    args = sys.argv
    command = args[1]
    port = int(args[2])
    address = ('localhost', port)
    if command == 'client':
        client(address)
    elif command == 'server':
        server(address)
    else:
        print('python channel.py <client|server>')
