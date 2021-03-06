import copy
from collections import deque
import numpy as np

from keras.preprocessing.text import text_to_word_sequence

indexer = dict()
def getIndex(word):
    if word not in indexer:
        indexer[word] = len(indexer)+1
    return indexer[word]

def sent2seq(sentence,length):
    seq = map(getIndex, text_to_word_sequence(sentence))
    return seq + [0]*(length-len(seq))

def initHist(state,hist_size=5,null=True):
    if null:
        states = [np.zeros(len(state), dtype="int") for _ in range(hist_size)]
        states[-1] = state
    else:
        states = [state for _ in range(hist_size)]
    history = deque(states,hist_size)
    return history

def addHistoryState(hist,state):
    hist2 = copy.copy(hist)
    hist2.append(state)
    return hist2
