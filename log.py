import sqlite3
import logging
import sys
import os
import time
import random

from channel import Channel
from sample import SQLiteHandler, DuplicateRecordError


def log_client(address):
    c = Channel()
    c.connect(address)

    while True:
        i = random.randint(0, 10)
        c.send(f"log value {i}".encode('utf-8'))
        try:
            res = c.recv()
        except:
            c.connect(address)
            print("reconnected")
            continue
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
            print('reconnecting')
            c.reconnect()
            print('reconnected')
            continue

        if msg == b'':
            print('waiting')
            time.sleep(1)
            continue

        try:
            log.critical(msg)
        except DuplicateRecordError:
            c.send(b'nack')
            continue

        c.send(b'ack')


if __name__ == '__main__':
    global address
    role = sys.argv[1]
    port = sys.argv[2]
    address = ('localhost', int(port))
    if role == 'client':
        log_client(address)
    if role == 'server':
        create_db()
        log_server(address)
