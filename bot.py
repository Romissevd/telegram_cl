import re

import telebot

from config import TOKEN
from matches import list_matches

# match = None
current_match = None
YES = 'Да'
NO = 'Нет'
GO = 'Поехали'
ERROR = 'Error.\nЧто-то пошло не так.'
text_go = 'Начнем?'
text_bye = 'Тогда прощай.\nЖду в следующий раз'
bad_result_match = 'Таких результатов не бывает!\nПринимаются значения вида X-X'

pattern_result_match = re.compile('\d{1}-\d{1}')
pattern_bad_result_match = re.compile('\d{2}-\d{1}|\d{1}-\d{2}|\d{2}-\d{2}')
bot = telebot.TeleBot(TOKEN)

keyboard_yes_or_no = telebot.types.ReplyKeyboardMarkup(True, True, True)
keyboard_yes_or_no.add(YES, NO)

del_keyboard = telebot.types.ReplyKeyboardRemove()


keyboard_go = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_go.row(GO)


go = telebot.types.InlineKeyboardButton('Поехали', callback_data='go')


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    text_message = 'Привет, {}!\n' \
                   'Я бот-чемпион, который принимает ставки на матчи Лиги Чемпионов по футболу.\n' \
                   'Хочешь сделать прогноз на матч?'.format(message.chat.username)
    bot.send_message(message.chat.id, text_message, reply_markup=keyboard_yes_or_no)


def generator_matches(list_matches):
    yield from list_matches


next_match = generator_matches(list_matches)


def text_matches():
    text = 'OK!\nСледующий тур - %s\nВ этом туре будут играть между собой такие пары...\n'
    for match in list_matches:
        text += match + '\n'
    return text


def save_current_match(match):
    global current_match
    current_match = match


def download_match():
    return current_match


@bot.message_handler(content_types=['text'])
# @bot.edited_message_handler(content_types=['text'])
def send_text(message):
    if message.text == YES:
        text_message = text_matches()
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
        bot.send_message(message.chat.id, text_go, reply_markup=keyboard_go)
    elif message.text == NO:
        bot.send_message(message.chat.id, text_bye, reply_markup=del_keyboard)
    elif message.text == GO:
        match = next(next_match)
        save_current_match(match)
        bot.send_message(message.chat.id, match, reply_markup=del_keyboard)
    elif re.match(pattern_result_match, message.text):
        bot.send_message(message.chat.id, 'Результат принят!')
        try:
            match = next(next_match)
            save_current_match(match)
            bot.send_message(message.chat.id, match)
        except StopIteration:
            bot.send_message(message.chat.id, 'Спасибо! Мы закончили. Удачи...')
    elif re.match(pattern_bad_result_match, message.text):
        bot.send_message(message.chat.id, bad_result_match, reply_to_message_id=message.message_id)
        bot.send_message(message.chat.id, download_match())
    else:
        text_message = ERROR
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)


bot.polling()
