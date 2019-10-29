import re

import telebot

from config import TOKEN
from matches import list_matches

YES = 'Да'
NO = 'Нет'
GO = 'Поехали'
ERROR = 'Error.\nЧто-то пошло не так.'
pattern_result_match = re.compile('\d{1}-\d{1}')
bot = telebot.TeleBot(TOKEN)
keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
del_keyboard = telebot.types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    text_message = 'Привет, {}!\n' \
                   'Я бот-чемпион, который принимает ставки на матчи Лиги Чемпионов по футболу.\n' \
                   'Хочешь сделать прогноз на матч?'.format(message.chat.username)
    keyboard.row(YES, NO)
    bot.send_message(message.chat.id, text_message, reply_markup=keyboard)


def generator_matches(list_matches):
    yield from list_matches


next_match = generator_matches(list_matches)


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def send_text(message):
    if message.text == YES:
        text_message = 'OK!\nСледующий тур - %s\nВ этом туре будут играть между собой такие пары...\n'
        for match in list_matches:
            text_message += match + '\n'
        bot.send_message(message.chat.id, text_message, reply_markup=keyboard)
        text_message = 'Начнем?'
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard1.row(GO)
        bot.send_message(message.chat.id, text_message, reply_markup=keyboard1)
    elif message.text == NO:
        text_message = 'Тогда прощай.\nЖду в следующий раз'
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
    elif message.text == GO:
        bot.send_message(message.chat.id, next(next_match))
    elif re.match(pattern_result_match, message.text):
        bot.send_message(message.chat.id, 'OK')
        try:
            bot.send_message(message.chat.id, next(next_match))
        except StopIteration:
            bot.send_message(message.chat.id, 'Спасибо! Мы закончили. Удачи...')
    else:
        text_message = ERROR
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)


bot.polling()
