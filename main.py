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
    name = None  # Название автомобиля
    vin = None  # вин автомобиля
    grade_body = None  # Оценка кузова
    rapids = None  # Пороги
    bottom_car = None  # Дно машины
    engine = None  # Двигатель
    suspension = None  # Подвеска
    transmission_type = None  # Тип трансмиссии
    transmission = None  # Коробка передач
    rudder = None  # Руль
    interior = None  # Интерьер
    documents = None  # Документы
    show_auto = None

    def clean_data(self):
        self.name = None
        self.vin = None
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


data = Data()


# Начинаем с входной команды
@bot.message_handler(commands=['help', 'start', 'go'])
def start(message):
    data.clean_data()
    mess = f'Начнем, {message.from_user.first_name}?'
    bot.send_message(message.chat.id, mess)
    bot.register_next_step_handler(message, get_user_text)


# Спрашиваем наименование авто подключаем и создаем БД и таблицу если ее нет.
def get_user_text(message):
    conn = sqlite3.connect('dataBase.sql')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS auto')

    cur.execute(
        'CREATE TABLE IF NOT EXISTS auto (id int auto_increment primary key, auto_name varchar(50), auto_vin varchar('
        '50), grade_body int, rapids varchar(30), bottom_car varchar(30), engine varchar(80),suspension varchar(50), '
        'transmission_type varchar(50), transmission varchar(50), rudder varchar(50), interior varchar(50), '
        'documents varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет, сейчас начнем осмотр')
    bot.send_message(message.chat.id, 'Введи наименование авто')
    bot.register_next_step_handler(message, auto_name)  # вызываем следующую ф-ю


# Сохраняем в глобальную переменную наименование авто, спрашиваем ВИН, и выз следующий пункт
def auto_name(message):
    global data
    data.name = message.text
    bot.send_message(message.chat.id, 'Отлично, теперь VIN автомобиля')
    bot.register_next_step_handler(message, auto_vin)


# Сохраняем ВИН и спрашиваем общую оценку кузова
def auto_vin(message):
    global data
    data.vin = message.text
    bot.send_message(message.chat.id, 'Кузов. Состояние по 5-ой шкале. Введи число')
    bot.register_next_step_handler(message, auto_grade)


# сохраняем оценку кузова и спрашиваю про пороги
def auto_grade(message):
    global data
    data.grade_body = message.text
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


# Интерьер в машине
def auto_interior(message):
    global data
    data.interior = message.text
    bot.send_message(message.chat.id, 'Документы. Напиши комментарий')
    bot.register_next_step_handler(message, insert_check_list)


# Подкл к БД, записываем полученные данные и выводим кнопку с результатом
def insert_check_list(message):
    global data
    data.documents = message.text

    conn = sqlite3.connect('dataBase.sql')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO auto (auto_name, auto_vin, grade_body, rapids, bottom_car, engine, suspension, "
        "transmission_type, transmission, rudder, interior, documents) VALUES ('%s','%s','%s','%s','%s','%s','%s',"
        "'%s','%s','%s','%s','%s')" % (
            data.name, data.vin, data.grade_body, data.rapids, data.bottom_car, data.engine, data.suspension,
            data.transmission_type, data.transmission, data.rudder,
            data.interior, data.documents))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Результат', callback_data='result'))
    bot.send_message(message.chat.id, 'Проверь результат', reply_markup=markup)


# Ловим запрос о результате и выводим через цикл работая с string
@bot.callback_query_handler(func=lambda call: True)
def result_auto(call):
    global data
    conn = sqlite3.connect('dataBase.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM auto")
    all_auto = cur.fetchall()

    data.show_auto = ''
    for el in all_auto:
        data.show_auto += f'Машина: {el[1]},\n VIN: {el[2]},\n Общая оценка кузова: {el[3]},\n Пороги: {el[4]},\n Дно машины: {el[5]},\n Двигатель: {el[6]},\n' \
                          f' Подвеска: {el[7]},\n Тип трансмиссии: {el[8]},\n Коробка передач: {el[9]},\n Руль: {el[10]},\n Интерьер: {el[11]},\n Документы: {el[12]}'

    cur.close()
    conn.close()

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
