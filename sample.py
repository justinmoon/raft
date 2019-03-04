import logging
import sqlite3


class FileHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        fmt = '%(levelname)-8s: %(message)s'
        formatter = logging.Formatter(fmt)
        self.setFormatter(formatter)

    def emit(self, record):
        print("record:", record)
        msg = self.format(record)
        print("msg:", msg)
        with open("log.txt", "a") as f:
            f.write(msg + '\n')


class SQLiteHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        fmt = '%(levelname)-8s: %(message)s'
        formatter = logging.Formatter(fmt)
        self.setFormatter(formatter)

    def emit(self, record):
        print("record:", record)
        msg = self.format(record)
        print("msg:", msg)
        with open("log.txt", "a") as f:
            f.write(msg + '\n')


def sqlite_demo():
    conn = sqlite3.connect('log.db')

    def create_table():
        conn.execute('''
        CREATE TABLE messages (level text, timestamp text, message text)
        ''')

    def record(message):
        q = '''
        INSERT INTO
            messages
        VALUES
            ("INFO", "today", "OMG")
        '''
        conn.execute(q)

    def query():
        return conn.execute("SELECT * FROM messages").fetchall()

    try:
        create_table()
    except:
        pass

    record("FIXME")
    record("FIXME")
    conn.commit()
    print(query())


def file_handler_demo():
    log = logging.getLogger(__name__)
    log.addHandler(FileHandler())
    log.error("OMG")


if __name__ == '__main__':
    sqlite_demo()
