import time

from stats import Stats
from collections import namedtuple

class Session:
    def __init__(self, session = {}):
        if (session == None):
            session = {}

        self.words = session.get('words', [])
        self.stats = Stats(session.get('stats'))
        self.duration = session.get('duration', 0)
        self.started = session.get('started', int(time.time()))
        self.finished = session.get('finished', int(time.time()))

    def updateStats(self, param):
        self.finished = int(time.time())
        self.stats.updateParam(param)

    def updateWords(self, word):
        self.words.append(word.get('key'))
        setWords = set(self.words)
        self.words = list(setWords)

    def updateDuration(self):
        self.duration = abs(int(self.started - self.finished))

    def getDict(self):
        return self.__dict__