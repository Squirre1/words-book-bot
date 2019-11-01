import flask
from rest import Requests
from collections import Counter
import os

http = Requests()

default_user = os.environ.get('TELEBOT_USER_ID')

def main(userId = default_user):
    sessions = http.get_sessions(userId)

    statistics = http.get_statistics(userId)
    if (statistics == None): return 'Statistics for this user is empty'

    return flask.render_template('main.html', statistics=statistics, sessions=sessions)
