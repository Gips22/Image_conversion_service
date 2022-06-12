import telebot

bot = telebot.TeleBot('5426658187:AAGAw5i0q7HTaImJnAtYHqvhDkyOxpyZkoA')

@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>'
    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler()
def get_user_text(message):
    if message.text == 'Hello':
        bot.send_message(message.chat.id, 'И тебе бонжур', parse_mode='html')
    elif message.text == 'id':
        bot.send_message(message.chat.id, f'Твой ID: {message.from_user.id}', parse_mode='html')
    elif message.text == 'photo':
        photo = open('/pic.png', 'rb')
        bot.send_message(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, 'Шо це робиш?', parse_mode='html')


bot.polling(none_stop=True)