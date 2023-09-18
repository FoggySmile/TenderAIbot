import telebot
from telebot import types

bot = telebot.TeleBot('6547518088:AAGmN6IT4KUfo6To9EhbwY5-OLo0j7aFHls')
selected_regions = []

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    selected_regions.clear()

    bot.send_message(message.chat.id, 'Здравствуйте!\nЭто чат-бот автоматизированного поиска тендеров по ключевым фильтрам со 100 основных площадок. Я помогу быстро и эффективно подобрать тендер.')
    keyboard = types.InlineKeyboardMarkup()
    button_start_search = types.InlineKeyboardButton('Начать поиск', callback_data='start_search')
    keyboard.add(button_start_search)
    
    bot.send_message(message.chat.id, 'Нажмите "Начать поиск" для начала поиска тендеров.', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'start_search')
def search(call):
    bot.send_message(call.message.chat.id, 'Пожалуйста, укажите регион текстом или кодом, в котором вы хотите найти тендеры.\n\nНапример: Москва, 60, 178, Сургут.')
    bot.register_next_step_handler(call.message, process_region)

selected_industry = None

@bot.message_handler(func=lambda message: True)
def process_region(message):
    region = message.text
    selected_regions.append(region)
    region_list = '\n'.join(selected_regions)
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
    global selected_industry
    selected_industry = industry
    
    keyboard = types.InlineKeyboardMarkup()
    button_44fz = types.InlineKeyboardButton('44 ФЗ', callback_data='44 ФЗ')
    button_223fz = types.InlineKeyboardButton('223 ФЗ', callback_data='223 ФЗ')
    button_commercial = types.InlineKeyboardButton('Коммерческие закупки', callback_data='Коммерческие закупки')
    keyboard.add(button_44fz, button_223fz, button_commercial)
    
    bot.send_message(message.chat.id, 'Выберите тип тендера, который вас интересует:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['44 ФЗ', '223 ФЗ', 'Коммерческие закупки'])
def choose_tender_type(call):
    global selected_type
    selected_type = call.data
    
    keyboard = types.InlineKeyboardMarkup()
    button_week = types.InlineKeyboardButton('Неделя', callback_data='Неделя')
    button_month = types.InlineKeyboardButton('Месяц', callback_data='Месяц')
    button_more_month = types.InlineKeyboardButton('Больше месяца', callback_data='Больше месяца')
    keyboard.add(button_week, button_month, button_more_month)

    bot.send_message(call.message.chat.id, 'Выберите срок подачи заявок:', reply_markup=keyboard)

selected_customer = None

@bot.callback_query_handler(func=lambda call: call.data in ['Неделя', 'Месяц', 'Больше месяца'])
def choose_deadline(call):
    global selected_customer
    global deadline
    deadline = call.data

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
    global selected_customer
    selected_customer = None
    bot.send_message(call.message.chat.id, f'Проверка данных для подбора тендера:\n\nРегионы: {", ".join(selected_regions)}\nОтрасль: {selected_industry}\nТип: {selected_type}\nСроки: {deadline}')
    
    keyboard = types.InlineKeyboardMarkup()
    button_confirm = types.InlineKeyboardButton('Все верно', callback_data='confirm')
    button_change = types.InlineKeyboardButton('Внести изменения', callback_data='change')
    keyboard.add(button_confirm, button_change)
    bot.send_message(call.message.chat.id, '❕ Пожалуйста, проверьте, все ли данные верны, и дайте знать, если нужно внести какие-либо изменения или начать поиск тендера с этими параметрами.', reply_markup=keyboard)

data_changed = False

@bot.message_handler(func=lambda message: True)
def process_customer(message):
    global selected_customer
    selected_customer = message.text
    if 'data_changed' not in globals():
        globals()['data_changed'] = False  # Инициализация флага в глобальной области видимости

    if globals().get('data_changed'):
        check_data(message.chat.id)
        globals()['data_changed'] = False  

def check_data(chat_id):
    global selected_regions
    global selected_industry
    global selected_type
    global deadline
    global selected_customer
    
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

bot.polling(none_stop=True)
