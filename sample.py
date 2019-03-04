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

        # SQLite stuff
        self.conn = sqlite3.connect('log.db')

    def emit(self, record):
        msg = self.format(record)
        q = '''
        INSERT INTO
            messages (message)
        VALUES
            (?)
        '''
        self.conn.execute(q, [msg])
        self.conn.commit()


def sqlite_demo():
    conn = sqlite3.connect('log.db')

    def create_table():
        conn.execute('''
        CREATE TABLE IF NOT EXISTS 
        messages (id integer primary key, level text, timestamp text, message text)
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

    create_table()
    record("FIXME")
    record("FIXME")
    conn.commit()
    print(query())


def sql_handler_demo():
    conn = sqlite3.connect('log.db')
    conn.execute('drop table messages')
    conn.execute('''
        CREATE TABLE messages (id integer primary key AUTOINCREMENT, message text)
    ''')
    conn.commit()

    log = logging.getLogger(__name__)
    log.addHandler(SQLiteHandler())
    log.critical("OMG")
    log.error("ZOMFG")
    print(conn.execute("SELECT * FROM messages").fetchall())


if __name__ == '__main__':
    sql_handler_demo()
    # log = logging.getLogger(__name__)
    # log.addHandler(SQLiteHandler())
    # log.error("OMG")
