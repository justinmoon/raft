import time
import queue
import signal
import random
import threading
import logging


logging.basicConfig(level="INFO", format='%(threadName)-6s | %(message)s')


class Log:
    pass


class Controller:
    pass


def run(q):

    # where's the controller?
    # who writes to the queue?
    # - presumably there are threads that do this
    # - how can a timer interrupt this?

    # q = queue.Queue()
    raft = RaftMachine()

    def alarm_handler(signum, frame):
        # FIXME
        if signum == signal.SIGALRM:
            print(f'calling for election from {threading.currentThread()}')

    # Set alarms for timeouts
    signal.signal(signal.SIGALRM, alarm_handler)

    while True:
        print('waiting for messages')
        msg_type, msg_data = q.get()
        print('got message', msg_type, msg_data)
        if msg_type == 'append_entries':
            raft.handle_append_entries(msg_data)
        elif msg_type == 'request_vote':
            raft.handle_request_vote(msg_data)


class RaftMachine:

    def __init__(self):
        self.state = Follower
        self.controller = Controller()
        self.log = Log()

        # Mystery params from the papaer
        self.current_term = 0
        self.voted_for = 0
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = []
        self.match_index = []

    def handle_timeout(self):
        self.controller.request_vote()

    def handle_request_vote(self, msg):
        self.current_term += 1
        vote_granted = True
        return self.current_term, vote_granted

    def handle_append_entries(self, msg):

        # If it's from our last leader, defer timeout
        if msg['leader_id'] == self.voted_for:
            signal.alarm(1)
        else:
            success = False
            return self.current_term, success

        success = self.state.handle_append_entries(msg)
        return self.current_term, success


class BaseState:

    @staticmethod
    def handle_append_entries(msg):
        pass


class Leader(BaseState):
    pass


class Follower(BaseState):
    pass


class Candidate(BaseState):
    pass


def test(q):
    while True:
        pause = random.random() * 2
        msg_data = {
            'leader_id': 0,
        }
        time.sleep(pause)
        q.put(('append_entries', msg_data))



def demo():
    q = queue.Queue()
    threading.Thread(target=test, args=(q,)).start()
    run(q)


if __name__ == '__main__':
    demo()
