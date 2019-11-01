import flask
import constants
from telebot import types
from bot_handlers import bot
import os

import pages

server = flask.Flask(__name__)


@server.route('/' + constants.token, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(
        flask.request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/', methods=["GET"])
def index():
    try:
        bot.remove_webhook()
        bot.set_webhook(
            url="https://{}.herokuapp.com/{}".format(constants.appName, constants.token))
    except Exception:
        print('Frontend only')

    return pages.main()


@server.route('/<userId>', methods=["GET"])
def indexByUser(userId):
    return pages.main(userId)

if __name__ == '__main__':
    try:
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
        # bot.remove_webhook()
        # bot.polling(none_stop=True)
    except KeyboardInterrupt:
        exit()
