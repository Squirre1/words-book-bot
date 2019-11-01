import telebot
import constants

bot = telebot.TeleBot(constants.token)

try:
    print(bot.get_me())
except Exception:
    print('Bot not connected')
