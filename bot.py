import re

import telebot

import matches
from config import TOKEN

users_data = {}
YES = 'Да'
NO = 'Нет'
GO = 'Поехали'
CHANGE = 'Изменить'
NEXT = 'Следующий'
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

button_change = telebot.types.InlineKeyboardButton(CHANGE, callback_data=CHANGE)
button_next = telebot.types.InlineKeyboardButton(NEXT, callback_data=NEXT)
keyboard_change = telebot.types.InlineKeyboardMarkup()
keyboard_change.add(button_change, button_next)


def username_definition(message):
    username = 'Неизвестный'
    if message.chat.username:
        username = message.chat.username
    elif message.chat.first_name:
        username = message.chat.first_name
        if message.chat.last_name:
            username += ' ' + message.chat.last_name
    return username


@bot.message_handler(commands=['help'])
def helper(message):
    help_text = '/start - начало работы с ботом;\n' \
                '/help - подсказки;\n' \
                '/result - просмотреть мои ставки;\n' \
                '/change - изменить результаты матчей;'
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in users_data.keys():
        list_matches = matches.loading_matches_from_db()
        users_data[message.chat.id] = {
            'next_match': generator_matches(list_matches),
            'list_matches': list_matches,
            'result': {},
        }

    start_message = 'Привет, {}!\n' \
                    'Я бот-чемпион, который принимает ставки на матчи Лиги Чемпионов по футболу.\n' \
                    'Хочешь сделать прогноз на матч?'.format(username_definition(message))
    bot.send_message(message.chat.id, start_message, reply_markup=keyboard_yes_or_no)


def generator_matches(list_matches):
    yield from list_matches


def text_list_matches(list_matches):
    text = 'OK!\nТы можешь сделать ставки на такие игровые пары:\n'
    for match in list_matches:
        text += match + '\n'
    return text


def save_current_match(message, match):
    users_data[message.chat.id]['current_match'] = match


def download_match(message):
    return users_data[message.chat.id].get('current_match')


@bot.message_handler(commands=['result'])
def result(message):
    user = users_data.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'Я тебя не знаю!')
    elif not user.get('result'):
        bot.send_message(message.chat.id, 'Еще нет результатов')
    else:
        text_user_result = ''
        for match, res in user.get('result').items():
            text_user_result += match + ' => ' + res + '\n'
        bot.send_message(message.chat.id, text_user_result)


@bot.message_handler(commands=['change'])
def change_result(message):
    user = users_data.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'Я тебя не знаю!')
    elif not user.get('result'):
        bot.send_message(message.chat.id, 'Еще нет результатов')
    else:
        change_match = generator_matches(user.get('result').keys())
        match = next(change_match)
        change_text = match + ' => ' + user.get('result')[match]
        bot.send_message(message.chat.id, change_text, reply_markup=keyboard_change)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == CHANGE:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Меняем')
    elif call.data == NEXT:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Следующий')


@bot.message_handler(content_types=['text'])
# @bot.edited_message_handler(content_types=['text'])
def send_text(message):
    if message.text == YES:
        text_message = text_list_matches(users_data[message.chat.id]['list_matches'])
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
        bot.send_message(message.chat.id, text_go, reply_markup=keyboard_go)
    elif message.text == NO:
        bot.send_message(message.chat.id, text_bye, reply_markup=del_keyboard)
    elif message.text == GO:
        match = next(users_data[message.chat.id]['next_match'])
        save_current_match(message, match)
        bot.send_message(message.chat.id, match, reply_markup=del_keyboard)
    elif re.match(pattern_result_match, message.text):
        users_data[message.chat.id]['result'][download_match(message)] = message.text
        bot.send_message(message.chat.id, 'Результат принят!')
        try:
            match = next(users_data[message.chat.id]['next_match'])
            save_current_match(message, match)
            bot.send_message(message.chat.id, match)
        except StopIteration:
            bot.send_message(message.chat.id, 'Спасибо! Твои результаты сохранены. Удачи...')
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
