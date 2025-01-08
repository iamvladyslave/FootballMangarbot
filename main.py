import os
from background import keep_alive  #импорт функции для поддержки работоспособности
import pip

pip.main(['install', 'pytelegrambotapi'])

import telebot
from telebot import types
import time

# Ваш токен
bot = telebot.TeleBot('7570511427:AAFqCLAEQqsGRN051tNF8QxZ10KONN0pPA4')

# Ваш username
ADMIN_USERNAME = '@romanMR7'

# Словарь для хранения ID сообщений, которые нужно удалить
sent_messages = {}

# Словарь для хранения данных пользователей
user_data = {}

about_me_text = ("Меня зовут [Ваше имя], и я футбольный агент! 🤖\n\n"
                 "📸 Вот немного о моей работе.")

about_pricing = ("💸 **Расценки**:\n- Мои расценки таковы ... \n-")

about_terms = ("👨‍💻 **Условия работы**:\n1. Мои условия работы таковы ... ")


# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id == 1042810675:
        show_tasks_panel_admin(message)
    else:
        show_main_menu(message)


# Команда /menu
@bot.message_handler(commands=['menu'])
def start(message):
    user_id = message.from_user.id
    show_tasks_panel(message)


# Команда /start
@bot.message_handler(commands=['tasks'])
def start(message):
    user_id = message.from_user.id
    show_tasks_panel(message)


# Команда /pricing
@bot.message_handler(commands=['pricing'])
def show_pricing(message):
    user_id = message.from_user.id
    pricing_message = bot.send_message(user_id, f"{about_pricing}")
    save_sent_message(user_id, pricing_message.message_id)
    show_back_button(message)


# Команда /terms
@bot.message_handler(commands=['terms'])
def show_terms(message):
    user_id = message.from_user.id
    terms_message = bot.send_message(user_id, f"{about_terms}")
    save_sent_message(user_id, terms_message.message_id)
    show_back_button(message)


# Команда /contact
@bot.message_handler(commands=['contact'])
def show_contact(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "📞 Укажите ваш возраст:")
    bot.register_next_step_handler(message, get_age)


def show_tasks_panel_admin(message):
    try:
        task_text = "Приветствую Админ! Что хотите исправить в боте:"
        panel = types.InlineKeyboardMarkup(row_width=2)
        panel.add(
            types.InlineKeyboardButton("Добавить 'Обо мне'",
                                       callback_data="edit1"),
            types.InlineKeyboardButton("Добавить фото", callback_data="edit2"),
            types.InlineKeyboardButton("Новые расценки",
                                       callback_data="edit3"),
            types.InlineKeyboardButton("Новые условия работы",
                                       callback_data="edit4"),
        )
        bot.send_message(message.chat.id, task_text, reply_markup=panel)
    except Exception as e:
        print(f"Ошибка в show_tasks_panel: {e}")


# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "about_me":
            photo_path = "download.png"  # Проверьте, существует ли этот файл
            try:
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(call.message.chat.id,
                                   photo,
                                   caption=about_me_text)
            except FileNotFoundError:
                bot.send_message(call.message.chat.id,
                                 "Файл download.png не найден!")

            # Панель с кнопками
            panel = types.InlineKeyboardMarkup(row_width=2)
            panel.add(
                types.InlineKeyboardButton("Расценки💸",
                                           callback_data="pricing"),
                types.InlineKeyboardButton("Условия работы👨‍💻",
                                           callback_data="terms"),
                types.InlineKeyboardButton("Связаться со мной📞",
                                           callback_data="contact"))
            bot.send_message(call.message.chat.id,
                             "Выберите действие ниже:",
                             reply_markup=panel)

        if call.data == "pricing":

            pricing_message = bot.send_message(call.message.chat.id,
                                               f"{about_pricing}")
            save_sent_message(call.message.chat.id, pricing_message.message_id)
            show_back_button(call.message, pricing_message)

        elif call.data == "terms":

            terms_message = bot.send_message(call.message.chat.id,
                                             f"{about_terms}")
            save_sent_message(call.message.chat.id, terms_message.message_id)
            show_back_button(call.message, terms_message)

        elif call.data == "contact":

            bot.send_message(call.message.chat.id, "📞 Укажите ваш возраст:")
            bot.register_next_step_handler(call.message, get_age)

        elif call.data == "back_to_menu":
            delete_previous_messages(
                call.message.chat.id
            )  # Удаляем старые сообщения перед возвратом

        elif call.data == "edit1":
            delete_previous_messages(call.message.chat.id)
            terms_message = bot.send_message(call.message.chat.id,
                                             "Давайте сделаем новое описание")
            bot.register_next_step_handler(call.message, update_about_me_text)
        elif call.data == "edit2":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(
                call.message.chat.id,
                "👨 Пожалуйста, загрузите новое фото для замены текущего.")
            bot.register_next_step_handler(call.message, receive_new_photo)
        elif call.data == "edit3":
            delete_previous_messages(call.message.chat.id)
            terms_message = bot.send_message(call.message.chat.id,
                                             "Указать новые расценки")
            bot.register_next_step_handler(call.message, update_pricing)
        elif call.data == "edit4":
            delete_previous_messages(call.message.chat.id)
            terms_message = bot.send_message(call.message.chat.id,
                                             "Обновить условия работы")
            bot.register_next_step_handler(call.message, update_terms)

    except Exception as e:
        print(f"Ошибка в обработке callback: {e}")


# Обработчик для всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Проверяем, не является ли текст командой или сообщением, связанным с действиями
    if message.text.lower() not in [
            '/start', '/menu', '/tasks', '/pricing', '/terms', '/contact'
    ]:
        # Возврат в основное меню
        show_tasks_panel(message)


def update_about_me_text(message):
    global about_me_text
    try:
        new_text = message.text
        if new_text.strip():  # Проверяем, что текст не пустой
            about_me_text = new_text
            bot.send_message(message.chat.id,
                             "✅ Текст 'Обо мне' успешно обновлен!")
            show_tasks_panel_admin(message)
        else:
            bot.send_message(
                message.chat.id,
                "⚠️ Текст не может быть пустым. Попробуйте еще раз:")
            bot.register_next_step_handler(message, update_about_me_text)
    except Exception as e:
        print(f"Ошибка в update_about_me_text: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_about_me_text)


def update_pricing(message):
    global about_pricing
    try:
        new_text_pricing = message.text
        if new_text_pricing.strip():  # Проверяем, что текст не пустой
            about_pricing = new_text_pricing
            bot.send_message(message.chat.id,
                             "✅ Текст 'Расценки' успешно обновлен!")
            show_tasks_panel_admin(message)
        else:
            bot.send_message(
                message.chat.id,
                "⚠️ Текст не может быть пустым. Попробуйте еще раз:")
            bot.register_next_step_handler(message, update_pricing)
    except Exception as e:
        print(f"Ошибка в update_pricing: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_pricing)


def update_terms(message):
    global about_terms
    try:
        new_text1 = message.text
        if new_text1.strip():  # Проверяем, что текст не пустой
            about_terms = new_text1
            bot.send_message(message.chat.id,
                             "✅ Текст 'Условия работы' успешно обновлен!")
            show_tasks_panel_admin(message)
        else:
            bot.send_message(
                message.chat.id,
                "⚠️ Текст не может быть пустым. Попробуйте еще раз:")
            bot.register_next_step_handler(message, update_terms)
    except Exception as e:
        print(f"Ошибка в update_terms: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_terms)


def receive_new_photo(message):
    try:
        if message.content_type == 'photo':
            file_id = message.photo[
                -1].file_id  # Берем фото с максимальным разрешением
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Сохраняем файл под именем download.png
            with open("download.png", "wb") as new_file:
                new_file.write(downloaded_file)

            bot.send_message(
                message.chat.id,
                "✅ Новое фото успешно загружено и сохранено как download.png.")
            show_tasks_panel_admin(message)
        else:
            bot.send_message(message.chat.id,
                             "⚠️ Пожалуйста, отправьте изображение.")
            bot.register_next_step_handler(message, receive_new_photo)
    except Exception as e:
        print(f"Ошибка в receive_new_photo: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при загрузке фото. Попробуйте еще раз.")
        bot.register_next_step_handler(message, receive_new_photo)


# Функция отображения главного меню
def show_main_menu(message):
    welcome_text = ("👋 Добро пожаловать в бота футбольного менеджера!\n\n"
                    "🎮 Чем я могу помочь:\n"
                    "- Узнайте больше обо мне.\n"
                    "- Посмотрите расценки.\n"
                    "- Свяжитесь со мной!")
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Кто я?", callback_data="about_me")
    markup.add(button)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# Функция отображения панели задач (без кнопки "Назад")
def show_tasks_panel(message):
    try:
        task_text = "Выберите действие ниже:"
        panel = types.InlineKeyboardMarkup(row_width=2)
        panel.add(
            types.InlineKeyboardButton("Расценки💸", callback_data="pricing"),
            types.InlineKeyboardButton("Условия работы👨‍💻",
                                       callback_data="terms"),
            types.InlineKeyboardButton("Связаться со мной📞",
                                       callback_data="contact"))
        bot.send_message(message.chat.id, task_text, reply_markup=panel)
    except Exception as e:
        print(f"Ошибка в show_tasks_panel: {e}")


# Функция отображения кнопки "Назад"
def show_back_button(message, previous_message_id=None):
    try:

        # Создаем кнопку "Назад"
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton("Назад",
                                          callback_data="back_to_menu")
        markup.add(back)

        # Отправляем кнопку "Назад"
        back_message = bot.send_message(message.chat.id,
                                        "Выберите действие:",
                                        reply_markup=markup)

        # Сохраняем ID сообщения для удаления при следующем действии
        save_sent_message(message.chat.id, back_message.message_id)

    except Exception as e:
        print(f"Ошибка в show_back_button: {e}")


# Функция для сохранения ID сообщений
def save_sent_message(chat_id, message_id):
    if chat_id not in sent_messages:
        sent_messages[chat_id] = []
    sent_messages[chat_id].append(message_id)


# Функция для удаления предыдущих сообщений
def delete_previous_messages(chat_id):
    try:
        if chat_id in sent_messages:
            for message_id in sent_messages[chat_id]:
                bot.delete_message(chat_id, message_id)
            sent_messages[chat_id] = []  # Очищаем список после удаления
    except Exception as e:
        print(f"Ошибка в delete_previous_messages: {e}")


# Функция обработки возраста
def get_age(message):
    try:
        age = int(message.text)
        user_data[message.chat.id] = {'age': age}  # Сохраняем возраст
        bot.send_message(message.chat.id,
                         f"Ваш возраст: {age}. Теперь напишите ваше имя:")
        bot.register_next_step_handler(message, get_name)
    except ValueError:
        bot.send_message(message.chat.id,
                         "Введите корректный возраст (число):")
        bot.register_next_step_handler(message, get_age)
    except Exception as e:
        print(f"Ошибка в get_age: {e}")


def get_name(message):
    try:
        name = message.text
        user_data[message.chat.id]['name'] = name  # Сохраняем имя
        bot.send_message(
            message.chat.id,
            f"Спасибо, {name}! Пожалуйста, поделитесь своим Telegram-контактом:",
            reply_markup=contact_share_markup())
    except Exception as e:
        print(f"Ошибка в get_name: {e}")


# Кнопка для отправки контакта
def contact_share_markup():
    try:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        contact_button = types.KeyboardButton("Поделиться контактом",
                                              request_contact=True)
        markup.add(contact_button)
        return markup
    except Exception as e:
        print(f"Ошибка в contact_share_markup: {e}")


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        if message.contact:
            # Извлекаем имя и возраст из словаря
            name = user_data.get(message.chat.id, {}).get('name', 'Не указано')
            age = user_data.get(message.chat.id, {}).get('age', 'Не указан')

            # Форматирование текста с HTML
            contact_info = ("<b>🚨 Новый контакт! 🚨</b>\n"
                            "<b>📱 Имя:</b> {0}\n"
                            "<b>🎂 Возраст:</b> {1}\n"
                            "<b>📞 Телефон:</b> {2}\n".format(
                                name, age, message.contact.phone_number))
            # Отправляем админу
            bot.send_message('1042810675', contact_info, parse_mode='HTML')

            # Подтверждение пользователю
            bot.send_message(message.chat.id,
                             "Спасибо! Ваш контакт успешно отправлен.",
                             reply_markup=types.ReplyKeyboardRemove())

            # Возврат в основное меню
            show_tasks_panel(message)
    except Exception as e:
        print(f"Ошибка в handle_contact: {e}")


keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
bot.polling(non_stop=True, interval=0)  #запуск бота




