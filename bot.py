import logging
import re

import telebot

import matches
from config import TOKEN
from db_data_users import MongoDB

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

db = MongoDB()

logging.basicConfig(filename='myLog.log', filemode='w', level=logging.INFO)

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


def set_info_about_user(message):
    username = message.chat.username
    if username == 'null':
        username = None

    first_name = message.chat.first_name
    if first_name == 'null':
        first_name = None

    last_name = message.chat.last_name
    if last_name == 'null':
        last_name = None

    return {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
    }


def get_username(user):
    username = user.get('username', None)
    if username:
        return username
    first_name = user.get('first_name', None)
    if first_name:
        last_name = user.get('last_name', None)
        if last_name:
            return first_name + ' ' + last_name
        return first_name
    return 'Гость'


def check_user_info(telegram_user_info, db_user_info):
    return telegram_user_info['username'] != db_user_info['username'] or \
           telegram_user_info['first_name'] != db_user_info['first_name'] or \
           telegram_user_info['last_name'] != db_user_info['last_name']


@bot.message_handler(commands=['help'])
def helper(message):
    help_text = '/start - начало работы с ботом;\n' \
                '/help - подсказки;\n' \
                '/result - просмотреть мои ставки;\n' \
                '/change - изменить результаты матчей;'
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    str_user_id = str(user_id)
    if user_id not in users_data.keys():
        list_matches = matches.loading_matches_from_db()
        users_data[user_id] = {
            'next_match': generator_matches([match['match'] for match in list_matches]),
            'change_match': None,
        }
    info_about_user = set_info_about_user(message)
    user = db.get_user_info(str_user_id)
    if not user:
        db.set_user_info(str_user_id, info_about_user)
        user = db.get_user_info(str_user_id)
        logging.info('Добавлен новый пользователь - {}'.format(get_username(user)))

    elif check_user_info(info_about_user, user):
        db.update_user_info(str_user_id, info_about_user)
        logging.info('Пользователь {old_username}, изменил свои данные.'.format(old_username=get_username(user)))
        user = db.get_user_info(str_user_id)

    start_message = 'Привет, {}!\n' \
                    'Я бот-чемпион, который принимает ставки на матчи Лиги Чемпионов по футболу.\n' \
                    'Хочешь сделать прогноз на матч?'.format(get_username(user))
    bot.send_message(user_id, start_message, reply_markup=keyboard_yes_or_no)


def generator_matches(list_matches):
    yield from list_matches


def save_current_match(message, match):
    users_data[message.chat.id]['current_match'] = match


def download_match(message):
    return users_data[message.chat.id].get('current_match')


@bot.message_handler(commands=['result'])
def result(message):
    users_data[message.chat.id]['current_match'] = None
    user = users_data.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'Я тебя не знаю!')
        return
    results_matches = db.get_results_matches(str(message.chat.id))
    if not results_matches:
        bot.send_message(message.chat.id, 'Еще нет результатов')
    else:
        text_user_result = ''
        for match in results_matches:
            text_user_result += match['match'] + ' => ' + match['result'] + '\n'
        bot.send_message(message.chat.id, text_user_result)


@bot.message_handler(commands=['change'])
def change_result(message):
    users_data[message.chat.id]['current_match'] = None
    user = users_data.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'Я тебя не знаю!')
    elif not db.get_change_matches(str(message.chat.id)):
        bot.send_message(message.chat.id, 'Еще нет результатов для изменения')
    else:
        if message.text == '/change':
            user['change_match'] = generator_matches(db.get_change_matches(str(message.chat.id)))
        try:
            match = next(user['change_match'])
            change_text = match['match'] + ' => ' + match['result']
            bot.send_message(message.chat.id, change_text, reply_markup=keyboard_change)
        except StopIteration:
            user['change_match'] = None
            bot.send_message(message.chat.id, 'Спасибо! Твои результаты изменены. Удачи...')


# @bot.message_handler(commands=['file'])
# def write_file(message):
#     excel_file.write_result_matches_in_excel()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == CHANGE:
        change_match = call.message.text.split(' => ')[0]
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=call.message.text + '\nВведите новый результат')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, print_text, change_match)  # call.message.json.text
    elif call.data == NEXT:
        try:
            change_result(call.message)
        except AttributeError:
            change_result(call)
    elif call.data == bad_result_match:
        bot.send_message(call.chat.id, bad_result_match, reply_to_message_id=call.message_id)
        bot.register_next_step_handler_by_chat_id(call.chat.id, print_text, call.text)


def print_text(message, change_match):
    if re.match(pattern_result_match, message.text):
        db.change_result_matches(str(message.chat.id), change_match, message.text)
        message.data = NEXT
        callback_inline(message)
    else:
        message.data = bad_result_match
        message.text = change_match
        callback_inline(message)


@bot.message_handler(content_types=['text'])
# @bot.edited_message_handler(content_types=['text'])
def send_text(message):
    user_id = str(message.chat.id)
    if message.text == YES:
        list_matches = db.get_matches(user_id)
        if not list_matches and not db.get_change_matches(user_id):
            db.set_matches(user_id, matches.loading_matches_from_db())
            list_matches = db.get_matches(user_id)
        if not list_matches:
            text_message = 'Ты уже сделал ставки на все возомжные матчи, чтобы посмотреть рузультаты введи' \
                           ' команду /result, чтобы изменить результат /change'
            bot.send_message(user_id, text_message, reply_markup=del_keyboard)
        else:
            text_message = 'OK!\nТы можешь сделать ставки на такие игровые пары:\n'
            text_message += db.get_text_list_matches(user_id)
            users_data[message.chat.id] = {
                'next_match': generator_matches([match['match'] for match in list_matches]),
                'change_match': None,
            }
            bot.send_message(user_id, text_message, reply_markup=del_keyboard)
            bot.send_message(user_id, text_go, reply_markup=keyboard_go)

    elif message.text == NO:
        bot.send_message(user_id, text_bye, reply_markup=del_keyboard)
    elif message.text == GO:
        users_data[message.chat.id]['change_match'] = None
        try:
            match = next(users_data[message.chat.id]['next_match'])
            save_current_match(message, match)
            bot.send_message(user_id, match, reply_markup=del_keyboard)
        except StopIteration:
            bot.send_message(user_id, 'Спасибо! Твои результаты сохранены. '
                                      'Для просмотра результатов введи /result, для изменения - /change'
                                      ' Удачи...')
    elif re.match(pattern_result_match, message.text) and download_match(message):
        users_data[message.chat.id]['change_match'] = None
        db.change_result_matches(user_id, download_match(message), message.text)
        bot.send_message(user_id, 'Результат принят!')
        message.text = GO
        send_text(message)
    elif re.match(pattern_bad_result_match, message.text) and download_match(message):
        bot.send_message(user_id, bad_result_match, reply_to_message_id=message.message_id)
        bot.send_message(user_id, download_match(message))
    else:
        text_message = ERROR
        if download_match(message):
            bot.send_message(user_id, bad_result_match, reply_to_message_id=message.message_id)
            bot.send_message(user_id, download_match(message))
        else:
            bot.send_message(user_id, text_message, reply_markup=del_keyboard)
            helper(message)


bot.polling()
