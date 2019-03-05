import logging
import sqlite3


class DuplicateRecordError(Exception):
    pass


def check_duplicates(msg):
    conn = sqlite3.connect('log.db')
    matches = conn.execute('select count(*) from messages where message = (?)',
                           (msg,)).fetchone()[0]
    if bool(matches):
        raise DuplicateRecordError()


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
        check_duplicates(msg)
        q = '''
        INSERT INTO
            messages (message)
        VALUES
            (?)
        '''
        self.conn.execute(q, [msg])
        self.conn.commit()
