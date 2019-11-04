import re

import telebot

import matches
from config import TOKEN

chat_id = {}
YES = 'Да'
NO = 'Нет'
GO = 'Поехали'
ERROR = 'Error.\nИзвини, я тебя не понимаю.'
text_go = 'Начнем?'
text_bye = 'Тогда прощай.\nЖду в следующий раз'
bad_result_match = 'Таких результатов не бывает!\nПринимаются значения вида X-X'

pattern_result_match = re.compile('^\d{1}-\d{1}$')
pattern_bad_result_match = re.compile('^\d{2}-\d{1}$|^\d{2}-\d{2}$|^\d{1}-\d{2}$')
bot = telebot.TeleBot(TOKEN)

keyboard_yes_or_no = telebot.types.ReplyKeyboardMarkup(True, True, True)
keyboard_yes_or_no.add(YES, NO)

del_keyboard = telebot.types.ReplyKeyboardRemove()

keyboard_go = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_go.row(GO)


def username_definition(message):
    username = 'Неизвестный'
    if message.chat.username:
        username = message.chat.username
    elif message.chat.first_name:
        username = message.chat.first_name
        if message.chat.last_name:
            username += ' ' + message.chat.last_name
    return username


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    if message.chat.id not in chat_id.keys():
        list_matches = matches.lst_match()
        next_match = generator_matches(list_matches)
        chat_id[message.chat.id] = {
            'next_match': next_match,
            'list_matches': list_matches,
        }

    text_message = 'Привет, {}!\n' \
                   'Я бот-чемпион, который принимает ставки на матчи Лиги Чемпионов по футболу.\n' \
                   'Хочешь сделать прогноз на матч?'.format(username_definition(message))
    bot.send_message(message.chat.id, text_message, reply_markup=keyboard_yes_or_no)


def generator_matches(list_matches):
    yield from list_matches


def text_list_matches(list_matches):
    text = 'OK!\nСледующий тур - %s\nВ этом туре будут играть между собой такие пары...\n'
    for match in list_matches:
        text += match + '\n'
    return text


def save_current_match(message, match):
    chat_id[message.chat.id]['current_match'] = match # через get


def download_match(message):
    return chat_id[message.chat.id]['current_match'] # через get


@bot.message_handler(content_types=['text'])
# @bot.edited_message_handler(content_types=['text'])
def send_text(message):
    if message.text == YES:
        text_message = text_list_matches(chat_id[message.chat.id]['list_matches'])
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
        bot.send_message(message.chat.id, text_go, reply_markup=keyboard_go)
    elif message.text == NO:
        bot.send_message(message.chat.id, text_bye, reply_markup=del_keyboard)
    elif message.text == GO:
        match = next(chat_id[message.chat.id]['next_match'])
        save_current_match(message, match)
        bot.send_message(message.chat.id, match, reply_markup=del_keyboard)
    elif re.match(pattern_result_match, message.text):
        bot.send_message(message.chat.id, 'Результат принят!')
        try:
            match = next(chat_id[message.chat.id]['next_match'])
            save_current_match(message, match)
            bot.send_message(message.chat.id, match)
        except StopIteration:
            bot.send_message(message.chat.id, 'Спасибо! Мы закончили. Удачи...')
    elif re.match(pattern_bad_result_match, message.text):
        bot.send_message(message.chat.id, bad_result_match, reply_to_message_id=message.message_id)
        bot.send_message(message.chat.id, download_match(message))
    else:
        text_message = ERROR
        if download_match(message):
            bot.send_message(message.chat.id, bad_result_match, reply_to_message_id=message.message_id)
            bot.send_message(message.chat.id, download_match(message))
        else:
            bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)


bot.polling()
