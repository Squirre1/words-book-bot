import time


class Stats:
    def __init__(self, stats={}):
        if (stats == None):
            stats = {}

        self.lastAsked = stats.get('lastAsked', 0)

        self.asked = stats.get('asked', 0)
        self.mistakes = stats.get('mistakes', 0)
        self.guessings = stats.get('guessings', 0)
        self.reminders = stats.get('reminders', 0)

        self.VVasked = stats.get('VVasked', 0)
        self.VVguessings = stats.get('VVguessings', 0)
        self.VVmistakes = stats.get('VVmistakes', 0)
        self.VVreminders = stats.get('VVreminders', 0)

    def updateParam(self, param):
        setattr(self, param, getattr(self, param) + 1)

        if(param == 'asked' or param == 'VVasked'):
            self.lastAsked = time.time()

    def getDict(self):
        return self.__dict__
