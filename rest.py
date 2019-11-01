import time
import constants

from stats import Stats
from session import Session
from firebase import firebase


class Requests:
    def __init__(self):
        self.firebase = firebase.FirebaseApplication(constants.firebase, None)

    def get_all_dictionary(self):
        dictionary = self.firebase.get('/dictionary/', None)
        return dictionary

    def get_active_word(self, user_id):
        verifiable_word = self.firebase.get(
            '/dictionary/{0}/active'.format(user_id), None)
        return verifiable_word

    def get_dictionary(self, user_id):
        dictionary = self.firebase.get(
            '/dictionary/{0}/words'.format(user_id), None)
        return dictionary

    def get_statistics(self, user_id, wordKey=False):
        if(wordKey):
            statistics = self.firebase.get(
                '/dictionary/{0}/statistics/{1}'.format(user_id, wordKey), None)
        else:
            statistics = self.firebase.get(
                '/dictionary/{0}/statistics'.format(user_id), None)
        return statistics

    def get_sessions(self, user_id):
        result = self.firebase.get('/dictionary/{0}/sessions'.format(user_id), None)
        return result

    def get_last_session(self, user_id):
        # make session from last session object
        last_session = self.firebase.get('/dictionary/{0}/active/session'.format(user_id), None)
        session = Session(last_session)

        # if difference between now and updated times in this session is huge
        pause = abs(int(time.time()) - int(session.finished))
        print('\npause: {0}\n'.format(pause))

        if (pause > 1000):
            # make duration as finished - created, update sessions
            session.updateDuration()
            self.update_sessions(user_id, session)
            # make, update and return new session
            session = Session()

        # self.update_last_session(user_id, session)
        return session

    def update_dictionary(self, user_id, data):
        result = self.firebase.patch(
            '/dictionary/{0}/words'.format(user_id), data)
        return result

    def update_active_word(self, user_id, verifiable_word):
        result = self.firebase.patch(
            '/dictionary/{0}/active'.format(user_id), verifiable_word)
        return result

    def update_last_session(self, user_id, session):
        session = session.getDict()
        session['stats'] = session['stats'].getDict()
        result = self.firebase.patch(
            '/dictionary/{0}/active/session'.format(user_id), session)
        return result

    def update_statistics(self, user_id, wordKey, stats):
        result = self.firebase.patch(
            '/dictionary/{0}/statistics'.format(user_id), {wordKey: stats.getDict()})
        return result

    def update_sessions(self, user_id, session):
        session = session.getDict()
        session['stats'] = session['stats'].getDict()
        result = self.firebase.patch(
            '/dictionary/{0}/sessions'.format(user_id), {session['started']: session})
        return result

    def update_word_stats_value(self, user_id, word, param):
        wordKey = word.get('key')

        if (word.get('viceVersa', False)):
            param = 'VV' + param

        wordStats = self.get_statistics(user_id, wordKey)
        stats = Stats(wordStats)
        stats.updateParam(param)
        self.update_statistics(user_id, wordKey, stats)

        session = self.get_last_session(user_id)
        session.updateStats(param)
        session.updateWords(word)
        self.update_last_session(user_id, session)

    def delete_word(self, word, user_id):
        self.firebase.delete('/dictionary/{0}/words'.format(user_id), word)
        self.firebase.delete(
            '/dictionary/{0}/statistics'.format(user_id), word)
