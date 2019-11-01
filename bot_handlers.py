# -*- coding: utf-8 -*-

# TODO
# Add sessions radar graph
# Start statistics analyze
# Counter commands (most asked, mistakes, reminders)
# Statistics asked / guessings, guessings / mistakes

import sys
import os
import time

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")

from bot import bot
from stats import Stats
from rest import Requests

from numpy import random

import constants
import recognize
import gtranslate

import threading

timer = None

http = Requests()


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    global timer
    timer = threading.Timer(sec, func_wrapper)
    timer.start()


def stop():
    global timer
    if (timer):
        timer.cancel()


def log(message, answer):
    from datetime import datetime
    print(
        '\n-----{0}-----'.format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("{0} {1}({2}):\n{3}".format(
        message.from_user.first_name,
        message.from_user.last_name,
        str(message.from_user.id),
        message.text
    ))
    print("\nBOT:\n{0}".format(answer))
    print('--------------------------\n')


def send_message(message, text):
    log(message, text)

    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            bot.send_message(message.chat.id, text[x:x+4096], parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


def askWord(message):
    def ask():
        user_id = message.from_user.id

        dictionary = http.get_dictionary(user_id)
        statistics = http.get_statistics(user_id)

        if (dictionary == None):
            handle_start(message)
            stop()
            return

        words = [w for w in list(dictionary.keys()) if abs(
            (float(statistics[w]['lastAsked']) if statistics.get(w, False) else 0) - time.time()) > 1000]

        def getPmistakes(w):
            if (statistics.get(w)):
                guessings = statistics[w].get('guessings', 0)
                asked = statistics[w].get('asked', 0)

                if (asked):
                    return 1 - (guessings/asked)

            return 1

        if(len(words) == 0):
            send_message(message, 'Try later! You have learned enough!')
            stop()
        else:
            words7 = random.choice(words, 7, replace=False) if len(
                words) > 7 else words
            mistakesP = [getPmistakes(w) for w in words7]
            sum_of_mistakes = sum(mistakesP)
            probability = [p / (sum_of_mistakes * 1.0) for p in mistakesP]

            print('\n-----')
            print('{0} => {1} => {2}'.format(
                len(dictionary), len(words), words7))
            print('-----')
            print('{0}\n{1}'.format(mistakesP, probability))
            print('=====\n\n')

            verifiable_word = {}
            verifiable_word['key'] = random.choice(words7, p=probability)

            wordKey = verifiable_word['key']

            verifiable_word['value'] = dictionary[wordKey]
            verifiable_word['viceVersa'] = bool(random.choice([True, False]))

            result = http.update_active_word(user_id, verifiable_word)

            if(result):
                print('ask: ', wordKey)

                http.update_word_stats_value(user_id, verifiable_word, 'asked')

                if(verifiable_word['viceVersa']):
                    send_message(message, 'Member *{0}*?'.format(verifiable_word['value']))
                else:
                    send_message(message, 'Member *{0}*?'.format(wordKey))

                stop()

    return ask


def translateWord(message, viceVersa=False):
    user_id = message.from_user.id
    wordKey = message.text.replace('?', '')

    dictionary = http.get_dictionary(user_id)

    word = dictionary.get(wordKey, '')

    if (word):
        print('remind: ', word if viceVersa else wordKey)

        statsWord = {}
        statsWord['key'] = wordKey
        statsWord['value'] = word
        statsWord['viseVersa'] = viceVersa

        http.update_word_stats_value(user_id, statsWord, 'reminders')

        if (viceVersa):
            send_message(message, random.choice(constants.translate) + wordKey)
        else:
            send_message(message, random.choice(constants.translate) + word)
    else:
        send_message(message, random.choice(constants.undefined) + word)


def addWord(message):
    [key, value] = message.text.split(' @ ')

    data = {}
    data[key] = value

    if (key and value):
        user_id = message.from_user.id

        result = http.update_dictionary(user_id, data)

        if (result):
            stats = Stats()
            http.update_statistics(user_id, key, stats)

            send_message(message, random.choice(constants.adding))


def guessTranslation(message, verifiable_word):
    user_id = message.from_user.id
    http.update_word_stats_value(user_id, verifiable_word, 'guessings')
    send_message(message, random.choice(constants.guess))
    set_interval(askWord(message), 10)


def wrongTranslation(message, verifiable_word):
    user_id = message.from_user.id
    http.update_word_stats_value(user_id, verifiable_word, 'mistakes')
    send_message(message, random.choice(constants.wrong))


@bot.message_handler(commands=['vocabulary'])
def handle_vocabulary(message):
    dictionary = http.get_dictionary(message.from_user.id)
    dictionarySTR = '\n'.join("|{:<15s} | {:<15s}|".format(key, val)
                              for (key, val) in sorted(dictionary.items()))
    send_message(message, dictionarySTR)


@bot.message_handler(commands=['start'])
def handle_start(message):
    send_message(message, constants.start)


@bot.message_handler(commands=['ask'])
def handle_ask(message):
    set_interval(askWord(message), 10)


@bot.message_handler(commands=['forgot'])
def handle_forgot(message):
    user_id = message.from_user.id
    word = message.text.replace('/forgot ', '')

    http.delete_word(word, user_id)
    send_message(message, random.choice(constants.forgot))


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    stop()
    send_message(message, constants.stop)


@bot.message_handler(commands=['help'])
def handle_text(message):
    send_message(message, constants.help)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    word = http.get_active_word(message.from_user.id)
    value = ''

    if (word != None):
        viceVersa = word.get('viceVersa', False)
        value = word.get('key', '') if viceVersa else word.get('value', '')
        print ('current: ', str(word), message.text)

    if ('@' in message.text):
        addWord(message)
    elif ('?' in message.text):
        translateWord(message)
    elif (str(message.text).lower() == str(value).lower()):
        guessTranslation(message, word)
    elif (word == None or word.get('key', '') == ''):
        send_message(message, constants.notAsked)
    elif (message.text == ':('):
        message.text = word.get('key', '')
        translateWord(message, viceVersa)
        set_interval(askWord(message), 10)
    else:
        wrongTranslation(message, word)

@bot.message_handler(content_types=['photo'])
def photo(message):
    try:
        fileID = message.photo[-1].file_id
        print ('fileID in the message =', fileID)

        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        src = './tests/' + fileID

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

            print('start recognize: ', src)

            words = recognize.get_words_on_photo(src, fileID)
            translations = gtranslate.translateWords(words)

            print('recognized pairs', translations)

            dictionarySTR = '\n'.join("{0} @ {1}".format(key, val)
                                for (key, val) in translations)

            send_message(message, dictionarySTR)
    except Exception as e:
        print(e)
        send_message(message, "Something went wrong")


if __name__ == '__main__':
    bot.polling(none_stop=True)
