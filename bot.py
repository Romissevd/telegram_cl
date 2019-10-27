import telebot

from config import TOKEN

YES = 'Да'
NO = 'Нет'
ERROR = 'Ошибочка вышла. Выбери правильную команду'
bot = telebot.TeleBot(TOKEN)
keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
del_keyboard = telebot.types.ReplyKeyboardRemove(True)
keyboard.row(YES, NO)


@bot.message_handler(commands=['start'])
def start_message(message):
    username = message.chat.username

    text_message = 'Hello, {}!\nХочешь сделать прогноз на матч?'.format(username)

    bot.send_message(message.chat.id, text_message, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == YES:
        text_message = 'OK!\nСледующий тур - %s\nВ этом туре будут играть между собой такие пары...'
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
        text_message = 'Начнем?'
        bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

    elif message.text == NO:
        text_message = 'Тогда прощай.\nЖду в следующий раз'
        bot.send_message(message.chat.id, text_message, reply_markup=del_keyboard)
    else:
        text_message = ERROR
        bot.send_message(message.chat.id, text_message, reply_markup=keyboard)


bot.polling()
