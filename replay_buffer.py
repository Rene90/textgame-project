"""
Data structure for implementing experience replay

Author: Patrick Emami
"""
from collections import deque
import random
import numpy as np

class ReplayBuffer(object):

    def __init__(self, buffer_size, random_seed=123):
        """
        The right side of the deque contains the most recent experiences
        """
        self.buffer_size = buffer_size
        self.count = 0
        self.buffer = deque()
        random.seed(random_seed)

    def add(self, s, a, r, t, s2):
        experience = (s, a, r, t, s2)
        if self.count < self.buffer_size:
            self.buffer.append(experience)
            self.count += 1
        else:
            self.buffer.popleft()
            self.buffer.append(experience)

    def size(self):
        return self.count

    def sample_batch(self, batch_size):
        batch = []

        if self.count < batch_size:
            batch = random.sample(self.buffer, self.count)
        else:
            batch = random.sample(self.buffer, batch_size)

        s_batch = np.array([_[0] for _ in batch])
        a_batch = np.array([_[1] for _ in batch])
        r_batch = np.array([_[2] for _ in batch])
        t_batch = np.array([_[3] for _ in batch])
        s2_batch = np.array([_[4] for _ in batch])

        return s_batch, a_batch, r_batch, t_batch, s2_batch

    def last_n_batch(self, batch_size):
        batch = []

        if self.count < batch_size:
            batch = self.buffer
        else:
            batch = self.buffer[-batch_size:]

        s_batch = np.array([_[0] for _ in batch])
        a_batch = np.array([_[1] for _ in batch])
        r_batch = np.array([_[2] for _ in batch])
        t_batch = np.array([_[3] for _ in batch])
        s2_batch = np.array([_[4] for _ in batch])

        return s_batch, a_batch, r_batch, t_batch, s2_batch

    def clear(self):
        self.deque.clear()
        self.count = 0

class PrioritizedReplayBuffer(object):

    def __init__(self, buffer_size, random_seed=123):
        """
        The right side of the deque contains the most recent experiences
        """
        self.buffer_size = buffer_size
        self.buffer_pos = deque([],buffer_size)
        self.buffer_neg = deque([],buffer_size)
        random.seed(random_seed)

    def add(self, s, a, r, t, s2):
        experience = (s, a, r, t, s2)
        # put transitions with negative reward in one buffer and positive ones in another
        if r <= 0:
            self.buffer_neg.append(experience)
        else:
            self.buffer_pos.append(experience)

    def size(self):
        return len(self.buffer_pos) + len(self.buffer_neg)

    def sample_batch(self, batch_size, p_ratio=0.25):
        batch = []
        pos_sample_size = int(batch_size * p_ratio)
        if pos_sample_size > len(self.buffer_pos):
            pos_sample_size = len(self.buffer_pos)

        neg_sample_size = batch_size - pos_sample_size
        if neg_sample_size > len(self.buffer_neg):
            neg_sample_size = len(self.buffer_neg)

        pos_batch = random.sample(self.buffer_pos, pos_sample_size)
        neg_batch = random.sample(self.buffer_neg, neg_sample_size)
        batch = pos_batch + neg_batch

        s_batch = np.array([_[0] for _ in batch])
        a_batch = np.array([_[1] for _ in batch])
        r_batch = np.array([_[2] for _ in batch])
        t_batch = np.array([_[3] for _ in batch])
        s2_batch = np.array([_[4] for _ in batch])

        return s_batch, a_batch, r_batch, t_batch, s2_batch

    def clear(self):
        self.buffer_pos.clear()
        self.buffer_neg.clear()


def softmax(y):
    e = np.exp(np.array(y))
    return (e/np.sum(e))

class PrioritizedReplayBuffer2(object):

    def __init__(self, buffer_size, random_seed=123):
        """
        The right side of the deque contains the most recent experiences
        """
        self.buffer_size = buffer_size
        self.buffer_pos = deque([],buffer_size)
        self.buffer_neg = deque([],buffer_size)
        random.seed(random_seed)

    def add(self, s, a, r, t, s2):
        experience = (s, a, r, t, s2)
        # put transitions with negative reward in one buffer and positive ones in another
        if r <= 0.5:
            self.buffer_neg.append(experience)
        else:
            self.buffer_pos.append(experience)

    def size(self):
        return len(self.buffer_pos) + len(self.buffer_neg)

    def sample_batch(self, batch_size, p_ratio=0.25):
        batch = []
        num_pos = len(self.buffer_pos)
        num_neg = len(self.buffer_neg)
        pos_sample_size = int(batch_size * p_ratio)
        if pos_sample_size > num_pos:
            pos_sample_size = num_pos

        neg_sample_size = batch_size - pos_sample_size
        if neg_sample_size > num_neg:
            neg_sample_size = num_neg
        if pos_sample_size:
            pr_rewards = np.array(map(lambda x: x[2], self.buffer_pos), np.float)
            pr_rewards = softmax(pr_rewards)
            pos_batch_idx = np.random.choice(num_pos, pos_sample_size, False, pr_rewards)
            pos_batch = np.array(self.buffer_pos)[pos_batch_idx]
            #pos_batch = random.sample(self.buffer_pos, pos_sample_size)
        else:
            pos_batch = np.array(())
        neg_batch_idx = np.random.choice(num_neg, neg_sample_size, False)
        neg_batch = np.array(self.buffer_neg)[neg_batch_idx]
        #neg_batch = np.random.choice(self.buffer_neg, neg_sample_size, False)
        #neg_batch = random.sample(self.buffer_neg, neg_sample_size)
        if pos_sample_size:
            batch = np.concatenate((pos_batch, neg_batch))
        else:
            batch = neg_batch
        #batch = pos_batch + neg_batch

        s_batch = np.array([_[0] for _ in batch])
        a_batch = np.array([_[1] for _ in batch])
        r_batch = np.array([_[2] for _ in batch])
        t_batch = np.array([_[3] for _ in batch])
        s2_batch = np.array([_[4] for _ in batch])

        return s_batch, a_batch, r_batch, t_batch, s2_batch

    def clear(self):
        self.buffer_pos.clear()
        self.buffer_neg.clear()
