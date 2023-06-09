# Импортируем нужные библиотеки
import telebot
from telebot import types
import sqlite3
import random
from os import remove
import configparser

# Наша разработка
import write_file
import doc_from_email

# Сохраняем ключи от бота и подлкючаемся к нему(ключ спрятать в другой файл)
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')
login = config.get('helper', 'user')
password = config.get('helper', 'passw')

api_bot = config.get('helper', 'api_token')
bot = telebot.TeleBot(api_bot)


# Создаем переменные для записи в бд (после изменить на json)
class Data:
    name = None  # auto name
    vin = None  # VIN auto
    check_auto_vin = None # check VIN
    grade_body = None
    rapids = None
    bottom_car = None
    engine = None
    suspension = None
    transmission_type = None
    transmission = None
    rudder = None
    interior = None
    documents = None
    show_auto = None
    change_ad = None
    count_dtp = None

    def clean_data(self):
        self.name = None
        self.vin = None
        self.check_auto_vin = None
        self.grade_body = None
        self.rapids = None
        self.bottom_car = None
        self.engine = None
        self.suspension = None
        self.transmission_type = None
        self.transmission = None
        self.rudder = None
        self.interior = None
        self.documents = None
        self.show_auto = None
        self.change_ad = None
        self.count_dtp = None

data = Data()


# 1 Начинаем с входной команды
@bot.message_handler(commands=['help', 'start', 'go'])
def start(message):
    mess = f'Начнем, {message.from_user.first_name}?'
    bot.send_message(message.chat.id, mess)
    bot.register_next_step_handler(message, get_user_text)


# 2 Спрашиваем наименование авто подключаем и создаем БД и таблицу если ее нет.
def get_user_text(message):
    bot.send_message(message.chat.id, 'Привет, сейчас начнем осмотр')
    bot.send_message(message.chat.id, 'Введи наименование авто')
    bot.register_next_step_handler(message, auto_name)  # вызываем следующую ф-ю


# 3 Сохраняем в глобальную переменную наименование авто, спрашиваем ВИН, и выз следующий пункт
def auto_name(message):
    global data
    data.name = message.text
    bot.send_message(message.chat.id, 'Отлично, теперь VIN автомобиля')
    bot.register_next_step_handler(message, auto_vin)


# 4 Сохраняем ВИН
def auto_vin(message):
    global data
    data.vin = message.text
    bot.send_message(message.chat.id, 'Проверка VIN номера. Да или нет')
    bot.register_next_step_handler(message, check_auto_vin)

# 5 Сохраням ответ и спрашиваем общую оценку кузова
def check_auto_vin(message):
    global data
    data.check_auto_vin = message.text
    bot.send_message(message.chat.id, 'Документы. Напиши комментарий')
    bot.register_next_step_handler(message, check_documents)

def check_documents(message):
    global data
    data.documents = message.text
    bot.send_message(message.chat.id, 'Кузов. Состояние по 5-ой шкале. Введи число')
    bot.register_next_step_handler(message, auto_grade)

# 6 сохраняем оценку кузова и спрашиваю про пороги
def auto_grade(message):
    global data
    data.grade_body = message.text
    bot.send_message(message.chat.id, 'Напиши количество ДТП')
    bot.register_next_step_handler(message, count_dtp)

def count_dtp(message):
    global data
    data.count_dtp = message.text
    bot.send_message(message.chat.id, 'Пороги. Состояние по 5-ой шкале. Введи число')
    bot.register_next_step_handler(message, auto_rapids)

# Сохраняем оценку порогов и спрашиваем
def auto_rapids(message):
    global data
    data.rapids = match_answer(message.text)
    bot.send_message(message.chat.id, 'Дно машины. Состояние по 5-ой шкале. Введи число')
    bot.register_next_step_handler(message, bottom_car)


# Оценка дна машины
def bottom_car(message):
    global data
    data.bottom_car = match_answer(message.text)
    bot.send_message(message.chat.id, 'Двигатель. Напиши комментарий')
    bot.register_next_step_handler(message, auto_engine)


# Меняем цифру на соответствующий текст
def match_answer(value):
    if value == '1':
        value = 'Под замену'
    elif value == '2':
        value = 'Ремонтопригодный'
    elif value == '3':
        value = 'Ремонтопригодный с выраженной коррозией'
    elif value == '4':
        value = 'Жучки'
    else:
        value = 'Отличное состояние'
    return value


# Мотор
def auto_engine(message):
    global data
    data.engine = message.text
    bot.send_message(message.chat.id, 'Подвеска. Напиши комментарий')
    bot.register_next_step_handler(message, auto_suspension)


# Подвеска
def auto_suspension(message):
    global data
    data.suspension = message.text
    bot.send_message(message.chat.id, 'Тип коробки передач.')
    bot.register_next_step_handler(message, transmission_type)


# Тип трансмиссии
def transmission_type(message):
    global data
    data.transmission_type = message.text
    bot.send_message(message.chat.id, 'Коробка передач. Напиши комментарий')
    bot.register_next_step_handler(message, auto_transmission)


# Коробка передач
def auto_transmission(message):
    global data
    data.transmission = message.text
    bot.send_message(message.chat.id, 'Руль. Напиши комментарий')
    bot.register_next_step_handler(message, auto_rudder)


# Руль
def auto_rudder(message):
    global data
    data.rudder = message.text
    bot.send_message(message.chat.id, 'Интерьер. Напиши комментарий')
    bot.register_next_step_handler(message, auto_interior)


# Изменения объявления
def auto_interior(message):
    global data
    data.interior = message.text
    bot.send_message(message.chat.id, 'Изменения объявления были?')
    bot.register_next_step_handler(message, insert_check_list)


# Подкл к БД, записываем полученные данные и выводим кнопку с результатом
def insert_check_list(message):
    global data
    data.change_ad = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Результат', callback_data='result'))
    bot.send_message(message.chat.id, 'Проверь результат', reply_markup=markup)


# Ловим запрос о результате и выводим через цикл работая с string
@bot.callback_query_handler(func=lambda call: True)
def result_auto(call):
    global data
    data.show_auto = f'1.Машина: {data.name},\n' \
                     f'2.VIN: {data.vin},\n ' \
                     f'3.Проверка VIN: {data.check_auto_vin},\n ' \
                     f'4.Документы: {data.documents},\n ' \
                     f'5.Общая оценка кузова: {data.grade_body},\n ' \
                     f'6.Кол-во ДТП: {data.count_dtp},\n ' \
                     f'7.Пороги: {data.rapids},\n ' \
                     f'8.Дно машины: {data.bottom_car},\n ' \
                     f'9.Руль: {data.rudder},\n ' \
                     f'10.Интерьер: {data.interior}, \n' \
                     f'11.Двигатель: {data.engine},\n' \
                     f'12.Подвеска: {data.suspension},\n ' \
                     f'13.Тип трансмиссии: {data.transmission_type},\n ' \
                     f'14.Коробка передач: {data.transmission},\n ' \
                     f'15.Изменение объявления: {data.change_ad}'

    bot.send_message(call.message.chat.id, data.show_auto)



# Сообщения фото сохраняем в папку
@bot.message_handler(content_types=['photo'])
def download_photo(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    random_name = str(random.randint(1, 100)) + fileID[1]
    downloaded_file = bot.download_file(file_info.file_path)
    # bot.send_message(message.chat.id, downloaded_file)
    with open(f"img/{random_name}.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)


# Запускаем функцию создания документа
@bot.message_handler(commands=['write'])
def write_new_file(message):
    global data
    write_file.write_files(data.name, data.show_auto)
    f = open(f'documents/{data.name}.docx','rb')
    bot.send_document(message.chat.id, f)


# Отправка документа на почту
@bot.message_handler(commands=['send'])
def write_new_file(message):
    global data
    doc_from_email.send_email(data.name, login, password)
    bot.send_message(message.chat.id, 'Отправили')
    remove(f'documents/{data.name}.docx')


bot.polling(none_stop=True)
