import threading
import queue
import logging
import random
import time

logging.basicConfig(level="INFO", format='%(threadName)-6s | %(message)s')


def target(thread_id, queues):
    thread_name = threading.currentThread().name
    while True:
        time.sleep(random.random() * 4)
        msg = f"thread {thread_name} says {random.randint(0,10)*random.randint(0,10)}"
        for i in range(5):
            if i != thread_id:
                queues[i].put(msg)


def run():
    queues = [queue.Queue() for _ in range(5)]

    threads = [
        threading.Thread(target=target, args=(i, queues))
        for i in range(5)
    ]

    for thread in threads:
        thread.start()

    while True:
        for i, q in enumerate(queues):
            print(f'(thread {i}) "{q.get()}"')
            time.sleep(.1)

if __name__ == '__main__':
    run()
