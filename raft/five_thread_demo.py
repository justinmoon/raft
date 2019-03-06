import threading
import queue
import logging
import random
import time

logging.basicConfig(level="INFO", format='%(threadName)-6s | %(message)s')


def send_msg(thread_id, queues, msg):
    for i in range(5):
        if i != thread_id:
            queues[i].put(msg)
            print("sent to ", i)


def heartbeat(thread_id, queues):
    print('inside heartbeat')

    # send the messages
    msg = {'command': 'append_entries', 'node_id': thread_id}
    send_msg(thread_id, queues, msg)

    # schedule the next heartbeat
    secs = random.random() * .7
    threading.Timer(secs, heartbeat, (thread_id, queues)).start()


def target(thread_id, queues):
    thread_name = threading.currentThread().name
    last_msg = time.time() + 100
    current_leader = None
    is_candidate = False
    voting_tally = [None] * 5

    # all threads need to spawn
    # one needs to request an election
    # others should accept their request, setting current_leader
    # when threshold crossed, start leading

    # node 0 calls election (hack)
    if thread_id == 0:
        msg = {'command': 'request_vote', 'candidate_id': 0}
        is_candidate = True
        send_msg(thread_id, queues, msg)
        print("SENT")

    while True:
        q = queues[thread_id]
        msg = q.get()
        print(thread_id, 'got', msg)

        if time.time() > last_msg + 1:
            raise TimeoutError()

        if msg['command'] == 'request_vote':
            res = {'command': 'respond_vote', 'node_id': thread_id, 'decision': True}
            queues[msg['candidate_id']].put(res)
            print(thread_id, 'voted for', msg['candidate_id'])

        if msg['command'] == 'respond_vote':
            if is_candidate:
                voting_tally[msg['node_id']] = msg['decision']
                if voting_tally.count(True) >= 2:  # FIXME: this should start from 3 w/ candidate voting for self
                    # set global variables
                    current_leader = thread_id
                    is_candidate = False
                    voting_tally = [None] * 5

                    print(thread_id, 'is now candidate')
                    msg = {'command': 'append_entries', 'node_id': thread_id}
                    send_msg(thread_id, queues, msg)
                    heartbeat(thread_id, queues)
                else:
                    print(msg['node_id'], 'voted for', thread_id)
            else:
                print('NOT A CANDIDATE')

        if msg['command'] == 'append_entries':
            # if msg['node_id'] == current_leader:
            print('received "append_entries" from', msg['node_id'])
            last_msg = time.time()


def run():
    queues = [queue.Queue() for _ in range(5)]

    threads = [
        threading.Thread(target=target, args=(i, queues))
        for i in range(5)
    ]

    for thread in threads:
        thread.start()

    # for thread in threads:
        # thread.join()


if __name__ == '__main__':
    run()
