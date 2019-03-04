import sqlite3
import logging
import sys
import os
import time

from channel import Channel
from sample import SQLiteHandler


def log_client(address):
    c = Channel()
    c.connect(address)
    c.send(b"very important configuration")
    res = c.recv()
    assert res == b'ack'
    print("received", res)
    time.sleep(1)


def inspect_db():
    conn = sqlite3.connect('log.db')
    contents = conn.execute('select * from messages').fetchall()
    return contents


def create_db():
    if os.path.exists('log.db'):
        os.remove('log.db')

    conn = sqlite3.connect('log.db')
    conn.execute('''
        CREATE TABLE messages (id integer primary key AUTOINCREMENT, message text)
    ''')
    conn.commit()


def log_server(address):
    log = logging.getLogger(__name__)
    log.addHandler(SQLiteHandler())

    c = Channel()
    c.accept(address)

    while True:
        try:
            msg = c.recv()
            print('received', msg)
        except:
            print("waiting")
            time.sleep(1)
            continue
        if msg == b'':
            print('waiting')
            time.sleep(1)
            continue
        log.critical(msg)
        c.send(b'ack')
        print('iteration')
        conn = sqlite3.connect('log.db')
        print(conn.execute('select * from messages').fetchall())
        conn.close()


if __name__ == '__main__':
    global address
    role = sys.argv[1]
    port = sys.argv[2]
    address = ('localhost', int(port))
    if role == 'client':
        log_client(address)
        print(inspect_db())
    if role == 'server': 
        create_db()
        log_server(address)

