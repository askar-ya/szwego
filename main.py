import telebot
import conf
import logic
from telebot import types

# создаем класс бота
bot = telebot.TeleBot(conf.BOT_TOKEN)


# обработчик команд
@bot.message_handler(commands=['start', 'add_shop', 'see_shops', 'by_date', 'one'])
def commands_proces(message):

    # получаем id юзера
    chat_id = message.chat.id

    """обрабатываем команды"""
    if message.text == '/start':
        bot.send_message(chat_id, 'Привет, выберите команду из меню!')

    elif message.text == '/add_shop':
        bot.send_message(chat_id, 'Отправьте ссылку на продавца!')
        bot.register_next_step_handler(message, get_shop)

    elif message.text == '/see_shops':

        # загружаем id магазинов
        shops = list(logic.read_file())

        for shop in shops:
            # Проходимся по списку магазинов

            # Создаем кнопку для удаления магазина
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Удалить', callback_data=f'dell {shop}'))

            # Отправляем сообщение
            bot.send_message(chat_id,
                             shop,
                             reply_markup=markup)

    elif message.text == '/by_date':
        markup = types.InlineKeyboardMarkup()
        for date in list(logic.get_dates()):
            markup.add(types.InlineKeyboardButton(date, callback_data=f'year_{date}'))
        markup.add(types.InlineKeyboardButton('за 24 часа', callback_data='day_last'))
        bot.send_message(chat_id, 'Выберите год или отправить за последние сутки', reply_markup=markup)
    elif message.text == '/one':
        bot.send_message(chat_id, 'Пришлите ссылку на товар')
        bot.register_next_step_handler(message, get_one)


# Обработчик call-back сигналов (кнопки)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    # получаем id юзера и текст ответа
    chat_id = call.message.chat.id
    call_back = call.data

    """Обрабатываем ответ"""
    if call_back.split(' ')[0] == 'dell':

        # Удаляем магазин из списка
        data = logic.read_file()
        del data[call_back.split(' ')[1]]
        logic.write_file(data)

        # Удаляем сообщение с кнопкой
        bot.delete_message(chat_id, call.message.id)

        # Уведомляем об успешном удалении магазина
        bot.send_message(chat_id, 'Магазин удален.')

    elif call_back == 'last':
        logic.send_shops(chat_id, '24')

    elif call_back.split('_')[0] == 'year':
        bot.delete_message(chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        year = call_back.split('_')[1]
        for date in list(logic.get_dates()[year]):
            markup.add(types.InlineKeyboardButton(date, callback_data=f'month_{date}_{year}'))
        bot.send_message(chat_id, 'Выберите месяц', reply_markup=markup)

    elif call_back.split('_')[0] == 'month':
        bot.delete_message(chat_id, call.message.id)
        year = call_back.split('_')[2]
        month = call_back.split('_')[1]
        markup = types.InlineKeyboardMarkup()
        for date in logic.get_dates()[year][month]:
            markup.add(types.InlineKeyboardButton(date, callback_data=f'day_{date}_{month}_{year}'))
        bot.send_message(chat_id, 'Выберите день', reply_markup=markup)

    elif call_back.split('_')[0] == 'day':

        bot.delete_message(chat_id, call.message.id)

        if call_back.split('_')[1] == 'last':
            date = 'last'
            call_data = 'sendЙ24Й'
        else:
            year = call_back.split('_')[3]
            month = call_back.split('_')[2]
            day = call_back.split('_')[1]
            date = f'{year} {month} {day}'
            call_data = f'sendЙ{year} {month} {day}Й'

        shops = list(logic.read_file())
        for shop in shops:
            if logic.check_date_shop(date, shop):

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Показать',
                                                      callback_data=call_data+shop))

                name = logic.get_shop_number(shop)
                if type(name) is str:
                    img = logic.get_shop_img(shop)
                    bot.send_photo(chat_id, img, caption=name, reply_markup=markup)
                else:
                    bot.send_photo(chat_id, name[0], reply_markup=markup)
        bot.send_message(chat_id, 'Это все подходящие магазины.')

    elif call_back.split('Й')[0] == 'send':
        print(call_back)
        date = call_back.split('Й')[1]

        logic.send_shops(chat_id, date, call_back.split('Й')[2])


def get_shop(message):
    """Функция второй стадии добавления магазина"""

    # Получаем ссылку на магазин и сохраняем id магазина
    shop_id = message.text.split('/')[-1:][0]
    res = logic.check_shop(shop_id)
    if res is not None:
        # Добавляем магазин в список
        logic.add_shop(shop_id)
        logic.pars_shop(shop_id)
        # Отправляем сообщение
        bot.send_message(message.chat.id, 'продавец добавлен')

        # Находим товары нового магазина
        logic.send_shops(message.chat.id, '24', shop_id)
    else:
        bot.send_message(message.chat.id, 'Ошибка в ссылке')


def get_one(message):

    item = logic.pars_one(message.text)
    if item is not None:
        logic.send_item(item, message.chat.id, item["shop"])
    else:
        bot.send_message(message.chat.id, 'Попробуйте другую ссылку')


# включаем луп
bot.polling(none_stop=True)