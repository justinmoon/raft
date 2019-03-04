import logging


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


def main():
    log = logging.getLogger(__name__)
    log.addHandler(FileHandler())
    log.error("OMG")

main()
