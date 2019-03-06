import time
import queue
import signal
import random
import threading
import logging


logging.basicConfig(level="INFO", format='%(threadName)-6s | %(message)s')

queues = [queue.Queue() for _ in range(5)]

class Log:
    pass


class Controller:

    def __init__(self, node_id):
        self.node_id = node_id
        self.timer = None
        # TODO: should I instantiate the RaftMachine here?

    def request_vote(self):
        # FIXME: there should be a timer associated with this
        msg = {
            "command": "request_vote",
            "node_id": self.node_id,
        }
        send_msg(self.node_id, msg)

    def vote(self, candidate_id, term, vote_granted):
        msg = {
            "command": "vote",
            "term": term,
            "vote_granted": vote_granted,
            "node_id": self.node_id,
        }
        queues[candidate_id].put(msg)
        print(f'Node {self.node_id} voted for {candidate_id}?: {vote_granted}')

    def send_heartbeat(self):
        print(f'Node {self.node_id} sent heartbeat')

        # Send heartbeat
        msg = {
            'command': 'append_entries',
            'node_id': self.node_id,
        }
        send_msg(self.node_id, msg)

        # Schedule next heartbeat
        threading.Timer(.5, self.send_heartbeat).start()

    def reset_timer(self):
        q = queues[self.node_id]
        if self.timer:  # FIXME
            self.timer.cancel()
        self.timer = threading.Timer(1, timeout, (q,))
        self.timer.start()

def timeout(q):
    msg = {
        'command': 'timeout',
    }
    q.put(msg)


# FIXME dumb function name. 
# Sounds like it would send to node_id, instead sends to everyone.
# Controller.broadcast would be a better name
def send_msg(node_id, msg):
    for i in range(5):
        if i != node_id:
            queues[i].put(msg)


def target(node_id):
    q = queues[node_id]
    raft_machine = RaftMachine(node_id)
    timer = None

    # node 0 starts us off FIXME 
    if node_id == 0:
        print("Node 0 requests vote")
        raft_machine.controller.request_vote()

    while True:
        # Get next message
        msg = q.get()

        # Handle the message
        handler = getattr(raft_machine, f'handle_{msg["command"]}')
        handler(msg)


def main():
    threads = []
    for node_id in range(5):
        thread = threading.Thread(target=target, args=(node_id,))
        thread.start()
        threads.append(thread)


class RaftMachine:

    def __init__(self, node_id):
        self.node_id = node_id
        self.state = Follower
        self.controller = Controller(node_id)
        self.log = Log()

        # Elections
        self.votes = [None] * 5

        # Mystery params from the papaer
        self.current_term = 0
        self.voted_for = 0
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = []
        self.match_index = []

    def handle_timeout(self, msg):
        self.controller.request_vote()

    def handle_request_vote(self, msg):
        self.votes[self.node_id] = True  # vote for themself
        self.current_term += 1
        vote_granted = True
        self.controller.vote(msg['node_id'], self.current_term, vote_granted)

    def handle_vote(self, msg):
        self.votes[msg['node_id']] = msg['vote_granted']

        y = len([v for v in self.votes if v is True])
        n = len([v for v in self.votes if v is False])

        # Election won
        if y > 2:
            self.votes = [None] * 5
            self.current_term += 1
            self.controller.send_heartbeat()

        # Election lost
        if n > 2:
            self.votes = [None] * 5

    def handle_append_entries(self, msg):

        # If it's from our last leader, defer timeout
        if msg['node_id'] == self.voted_for:
            self.controller.reset_timer()
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


if __name__ == '__main__':
    main()
