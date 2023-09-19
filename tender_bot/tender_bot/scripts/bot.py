import telebot
from telebot import types

bot = telebot.TeleBot('Спросите автора')
bot.user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.user_data[chat_id] = {
        'selected_regions': [],
        'selected_industry': None,
        'selected_type': None,
        'deadline': None,
        'selected_customer': None
    }

    bot.send_message(message.chat.id, 'Здравствуйте!\nЭто чат-бот автоматизированного поиска тендеров по ключевым фильтрам со 100 основных площадок. Я помогу быстро и эффективно подобрать тендер.')
    keyboard = types.InlineKeyboardMarkup()
    button_start_search = types.InlineKeyboardButton('Начать поиск', callback_data='start_search')
    keyboard.add(button_start_search)
    
    bot.send_message(message.chat.id, 'Нажмите "Начать поиск" и приступите к подбору тендоров.', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'start_search')
def search(call):
    bot.send_message(call.message.chat.id, 'Пожалуйста, укажите регион текстом или кодом, в котором вы хотите найти тендеры.\n\nНапример: Москва, 60, 178, Сургут.')
    bot.register_next_step_handler(call.message, process_region)

selected_industry = None

def process_region(message):
    region = message.text
    
    # Получаем chat_id текущего пользователя
    chat_id = message.chat.id
    
    # Получаем текущий словарь данных пользователя из bot.user_data или создаем его, если еще не существует
    user_data = bot.user_data.get(chat_id, {})
    
    selected_regions = user_data.get('selected_regions', [])
    selected_regions.append(region)
    user_data['selected_regions'] = selected_regions

    # Обновляем данные пользователя в bot.user_data
    bot.user_data[chat_id] = user_data
    region_list = '\n'.join(user_data['selected_regions'])

    bot.send_message(message.chat.id, f"Вы выбрали регион(ы):\n{region_list}\n\n❕Если вы хотите добавить еще один регион, нажмите соответствующую кнопку.")

    keyboard = types.InlineKeyboardMarkup()
    button_add_region = types.InlineKeyboardButton('Добавить регион', callback_data='add_region')
    button_continue = types.InlineKeyboardButton('Продолжить', callback_data='continue')
    keyboard.add(button_add_region, button_continue)
    bot.send_message(message.chat.id, 'Выберите одно из действий:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'add_region')
def add_region(call):
    bot.send_message(call.message.chat.id, 'Введите регион текстом или кодом:')
    # Регистрация обработчика для добавления региона
    bot.register_next_step_handler(call.message, process_region)

@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def continue_search(call):
    bot.send_message(call.message.chat.id, 'Уточните отрасль, которая вас интересует.\nЭто поможет найти тендеры, наиболее соответствующие вашим областям экспертизы или интересам.')
    bot.register_next_step_handler(call.message, process_industry)

def process_industry(message):
    industry = message.text
    chat_id = message.chat.id
    user_data = bot.user_data.get(chat_id, {})
    user_data['selected_industry'] = industry
    # Обновляем данные пользователя в bot.user_data
    bot.user_data[chat_id] = user_data
    
    keyboard = types.InlineKeyboardMarkup()
    button_44fz = types.InlineKeyboardButton('44 ФЗ', callback_data='44 ФЗ')
    button_223fz = types.InlineKeyboardButton('223 ФЗ', callback_data='223 ФЗ')
    button_commercial = types.InlineKeyboardButton('Коммерческие закупки', callback_data='Коммерческие закупки')
    keyboard.add(button_44fz, button_223fz, button_commercial)
    
    bot.send_message(message.chat.id, 'Выберите тип тендера, который вас интересует:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['44 ФЗ', '223 ФЗ', 'Коммерческие закупки'])
def choose_tender_type(call):
    chat_id = call.message.chat.id
    # Получаем текущий словарь данных пользователя из bot.user_data или создаем его, если еще не существует
    user_data = bot.user_data.get(chat_id, {})
    # Обновляем значение selected_type в словаре данных пользователя
    user_data['selected_type'] = call.data
    # Обновляем данные пользователя в bot.user_data
    bot.user_data[chat_id] = user_data

    keyboard = types.InlineKeyboardMarkup()
    button_week = types.InlineKeyboardButton('Неделя', callback_data='Неделя')
    button_month = types.InlineKeyboardButton('Месяц', callback_data='Месяц')
    button_more_month = types.InlineKeyboardButton('Больше месяца', callback_data='Больше месяца')
    keyboard.add(button_week, button_month, button_more_month)

    bot.send_message(call.message.chat.id, 'Выберите срок подачи заявок:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['Неделя', 'Месяц', 'Больше месяца'])
def choose_deadline(call):
    chat_id = call.message.chat.id
    # Получаем текущий словарь данных пользователя из bot.user_data или создаем его, если еще не существует
    user_data = bot.user_data.get(chat_id, {})
    # Обновляем значение deadline в словаре данных пользователя
    user_data['deadline'] = call.data
    bot.user_data[chat_id] = user_data
    # Получаем значения из user_data для данного пользователя
    selected_customer = user_data.get('selected_customer', None)

    if selected_customer:  # Если заказчик уже выбран
        bot.register_next_step_handler(call.message, process_customer)
    else:
        keyboard = types.InlineKeyboardMarkup()
        button_skip = types.InlineKeyboardButton('Пропустить', callback_data='skip_customer')
        keyboard.add(button_skip)
        bot.send_message(call.message.chat.id, 'Если вы хотите найти тендеры от определенного заказчика, напишите полное название или выберите "Пропустить":', reply_markup=keyboard)
        bot.register_next_step_handler(call.message, process_customer)

@bot.callback_query_handler(func=lambda call: call.data == 'skip_customer')
def skip_customer(call):
    chat_id = call.message.chat.id
    
    # Получаем словарь данных пользователя из bot.user_data или создаем его, если он еще не существует
    user_data = bot.user_data.get(chat_id, {})
    
    # Получаем значения из user_data для данного пользователя; если user_data не существует, используем значения по умолчанию
    selected_regions = user_data.get('selected_regions', [])
    selected_industry = user_data.get('selected_industry')
    selected_type = user_data.get('selected_type')
    deadline = user_data.get('deadline')
    selected_customer = user_data.get('selected_customer')
    
    bot.send_message(chat_id, f'Проверка данных для подбора тендера:\n\nРегионы: {", ".join(selected_regions)}\nОтрасль: {selected_industry}\nТип: {selected_type}\nСроки: {deadline}\nОрганизация: {selected_customer}')
    
    keyboard = types.InlineKeyboardMarkup()
    button_confirm = types.InlineKeyboardButton('Все верно', callback_data='confirm')
    button_change = types.InlineKeyboardButton('Внести изменения', callback_data='change')
    keyboard.add(button_confirm, button_change)
    bot.send_message(chat_id, '❕ Пожалуйста, проверьте, все ли данные верны, и дайте знать, если нужно внести какие-либо изменения или начать поиск тендера с этими параметрами.', reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def process_customer(message):
    chat_id = message.chat.id
    user_data = bot.user_data.get(chat_id, {})
    user_data['selected_customer'] = message.text
    bot.user_data[chat_id] = user_data

    global data_changed
    data_changed = True

    if data_changed:
        check_data(message.chat.id)
        data_changed = False

def check_data(chat_id):
    user_data = bot.user_data.get(chat_id, {})
    # Получаем значения из bot.user_data для данного пользователя
    selected_regions = user_data.get('selected_regions', [])
    selected_industry = user_data.get('selected_industry', '-')
    selected_type = user_data.get('selected_type', '-')
    deadline = user_data.get('deadline', '-')
    selected_customer = user_data.get('selected_customer', '-')
    
    bot.send_message(chat_id, f'Проверка данных для подбора тендера:\n\nРегионы: {", ".join(selected_regions)}\nОтрасль: {selected_industry}\nТип: {selected_type}\nСроки: {deadline}\nОрганизация: {selected_customer}')
    
    keyboard = types.InlineKeyboardMarkup()
    button_confirm = types.InlineKeyboardButton('Все верно', callback_data='confirm')
    button_change = types.InlineKeyboardButton('Внести изменения', callback_data='change')
    keyboard.add(button_confirm, button_change)
    bot.send_message(chat_id, '❕ Пожалуйста, проверьте, все ли данные верны, и дайте знать, если нужно внести какие-либо изменения или начать поиск тендера с этими параметрами.', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['confirm', 'change'])
def final_check(call):
    if call.data == 'confirm':
        bot.send_message(call.message.chat.id, 'Поиск тендеров будет начат с указанными параметрами.')
        message_text1 = '🔹<a href="https://www.roseltorg.ru/procedure/32312766646">(Лот 1) Выполнение комплекса отделочных работ в притоннельных и пристанционных выработках станции "Театральная"</a>\n\nНомер лот - 32312766646\nНазвание площадки проведения - 44-ФЗ Электронный аукцион\nЗаказчик - АО “Метрострой Северной Столицы”\nРегион: Санкт-Петербург\nОкончание приема заявок - 27.09.2023 12:00:00\n\n3 874 297 РУБ'
        bot.send_message(call.message.chat.id, message_text1, parse_mode="HTML")
        message_text2 = '🔹<a href="https://www.roseltorg.ru/procedure/32312764310">(Лот 2) Выполнение комплекса работ по возведению внутренних конструкций и отделочным работам в притоннельных выработках от ПК 267+35,906 до ПК 285+88,349 на объекте: «Строительство Красносельско-Калининской линии от станции «Казаковская» до станции «Обводный канал 2» с электродепо «Красносельское»</a>\n\nНомер лот - 32312764310\nНазвание площадки проведения - Корпоративные закупки и закупки по 223-ФЗ\nЗаказчик - АО “Метрострой Северной Столицы”\nРегион: Санкт-Петербург\nОкончание приема заявок - 27.09.2023 12:00:00\n\n21 664 748 РУБ'
        bot.send_message(call.message.chat.id, message_text2, parse_mode="HTML")

    else:
        keyboard = types.InlineKeyboardMarkup()
        button_region = types.InlineKeyboardButton('Регион', callback_data='change_region')
        button_industry = types.InlineKeyboardButton('Отрасль', callback_data='change_industry')
        button_type = types.InlineKeyboardButton('Тип', callback_data='change_type')
        button_deadline = types.InlineKeyboardButton('Сроки', callback_data='change_deadline')
        button_customer = types.InlineKeyboardButton('Организация', callback_data='change_customer')
        keyboard.add(button_region, button_industry, button_type, button_deadline, button_customer)
        bot.send_message(call.message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'change_region')
def change_region(call):
    bot.send_message(call.message.chat.id, 'Введите новый регион текстом или кодом:')
    bot.register_next_step_handler(call.message, process_region)
    data_changed = True 

@bot.callback_query_handler(func=lambda call: call.data == 'change_industry')
def change_industry(call):
    bot.send_message(call.message.chat.id, 'Уточните новую отрасль, которая вас интересует:')
    bot.register_next_step_handler(call.message, process_industry)
    data_changed = True 

@bot.callback_query_handler(func=lambda call: call.data == 'change_type')
def change_type(call):
    keyboard = types.InlineKeyboardMarkup()
    button_44fz = types.InlineKeyboardButton('44 ФЗ', callback_data='44 ФЗ')
    button_223fz = types.InlineKeyboardButton('223 ФЗ', callback_data='223 ФЗ')
    button_commercial = types.InlineKeyboardButton('Коммерческие закупки', callback_data='Коммерческие закупки')
    keyboard.add(button_44fz, button_223fz, button_commercial)
    bot.send_message(call.message.chat.id, 'Выберите новый тип тендера:', reply_markup=keyboard)
    data_changed = True 

@bot.callback_query_handler(func=lambda call: call.data == 'change_deadline')
def change_deadline(call):
    keyboard = types.InlineKeyboardMarkup()
    button_week = types.InlineKeyboardButton('Неделя', callback_data='Неделя')
    button_month = types.InlineKeyboardButton('Месяц', callback_data='Месяц')
    button_more_month = types.InlineKeyboardButton('Больше месяца', callback_data='Больше месяца')
    keyboard.add(button_week, button_month, button_more_month)
    bot.send_message(call.message.chat.id, 'Выберите новый срок подачи заявок:', reply_markup=keyboard)
    data_changed = True 

@bot.callback_query_handler(func=lambda call: call.data == 'change_customer')
def change_customer(call):
    bot.send_message(call.message.chat.id, 'Введите новое название организации:')
    bot.register_next_step_handler(call.message, process_customer)
    data_changed = True 

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Бот остановлен.')


if __name__ == '__main__':
    bot.polling(none_stop=True)
