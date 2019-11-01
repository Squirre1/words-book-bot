# -*- coding: utf-8 -*-
import os

appName = 'memberries-vocabulary'
token = os.environ.get('TELEBOT_TOKEN')
firebase = os.environ.get('FIREBASE_APP')

help = """
--- Messages ---
*Tree?* - memberries remind you about translation for Tree
*Tree @ Дерево* - memberries add this couple in your dictionary
:( - answer it if you forgot asked word

--- Commands ---
/ask - memberries will ask your words
/vocabulary - memberries remind your vocabulary
/forgot Tree - memberries get rid of Tree in your dictionary
"""


start = """
Firstly, you should add pair of words
in your vocabulary in format key @ value

After that use /ask and memberries will ask your words

Example: Tree @ Дерево

Periodically, memberries will ask: 'Member *Tree*?'
You should answer: 'Дерево'

That's all! Use /help for information.
"""

stop = """
Okay, let me know. Write /start if you miss me
"""

notAsked = """
I haven\'t asked you. Use /start for it
"""

guess = [
    'Yeeeah',
    'Of course',
    'Ooo, I member',
    'Ooooh! Me too!',
    'Keep in mind it',
    'Sweet! Remember it',
    'Yeee, I member, member'
]

wrong = [
    'Uh-uh',
    'Wrong!',
    'Nooope',
    'Try again?',
    'Are you sure?',
    'No, you forgot :(',
    'No. No. No, it doesn\'t.',
]

translate = [
    'Remember that: ',
    'Oooh, remember: ',
    'Keep in mind that: ',
    'It\'s okay. Remember: ',
    'It\'s no big deal. Don\'t forget: ',
]

adding = [
    'I\'ve done it',
    'Already remember',
    'Okay! I will member it!',
]

forgot = [
    'Okay!',
    'I\'ve done it',
    'Already forgot',
]

undefined = [
    'No, I lose it :(',
    'I don\'t know that',
    'See /help for instructions.',
    'It\'s joke? You have never told me it.',
]
