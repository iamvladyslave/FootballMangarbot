from flask import Flask
import telebot
from telebot import types
from threading import Thread

# Ваш токен
bot = telebot.TeleBot('8087901925:AAH2cQ1f3O_dyL-uFCyDYz20PYkC6KsXt_o')

# Ваш username
ADMIN_USERNAME = '@vVv_075'

# Словарь для хранения ID сообщений, которые нужно удалить
sent_messages = {}

# Создаем Flask-приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"  # Простой endpoint для проверки состояния

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message)

# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "about_me":
            about_text = (
                "Меня зовут [Ваше имя], и я специализируюсь на создании Telegram-ботов! 🤖\n\n"
                "📸 Вот немного о моей работе."
            )
            photo_path = "download.png"  # Проверьте, существует ли этот файл
            try:
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo, caption=about_text)
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "Файл download.png не найден!")

            # Панель с кнопками
            panel = types.InlineKeyboardMarkup(row_width=2)
            panel.add(
                types.InlineKeyboardButton("Расценки💸", callback_data="pricing"),
                types.InlineKeyboardButton("Условия работы👨‍💻", callback_data="terms"),
                types.InlineKeyboardButton("Связаться со мной📞", callback_data="contact")
            )
            bot.send_message(call.message.chat.id, "Выберите действие ниже:", reply_markup=panel)

        elif call.data == "pricing":
            # Удаляем старые сообщения перед отправкой нового
            delete_previous_messages(call.message.chat.id)
            pricing_message = bot.send_message(call.message.chat.id, "💸 **Расценки**:\n- Создание бота: от $50.\n- Доработка: от $20.")
            save_sent_message(call.message.chat.id, pricing_message.message_id)
            show_back_button(call.message)

        elif call.data == "terms":
            # Удаляем старые сообщения перед отправкой нового
            delete_previous_messages(call.message.chat.id)
            terms_message = bot.send_message(call.message.chat.id, "👨‍💻 **Условия работы**:\n1. Полная предоплата.\n2. Сроки оговариваются заранее.")
            save_sent_message(call.message.chat.id, terms_message.message_id)
            show_back_button(call.message)

        elif call.data == "contact":
            # Удаляем старые сообщения перед отправкой нового
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "📞 Укажите ваш возраст:")
            bot.register_next_step_handler(call.message, get_age)

        elif call.data == "back_to_menu":
            # Удаляем старые сообщения перед возвратом в меню
            delete_previous_messages(call.message.chat.id)
            show_tasks_panel(call.message)

    except Exception as e:
        print(f"Ошибка в обработке callback: {e}")

# Функция отображения главного меню
def show_main_menu(message):
    welcome_text = (
        "👋 Добро пожаловать в бота футбольного менеджера!\n\n"
        "🎮 Чем я могу помочь:\n"
        "- Узнайте больше обо мне.\n"
        "- Посмотрите расценки.\n"
        "- Свяжитесь со мной!"
    )
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
            types.InlineKeyboardButton("Условия работы👨‍💻", callback_data="terms"),
            types.InlineKeyboardButton("Связаться со мной📞", callback_data="contact")
        )
        bot.send_message(message.chat.id, task_text, reply_markup=panel)
    except Exception as e:
        print(f"Ошибка в show_tasks_panel: {e}")

# Функция для добавления кнопки "Назад"
def show_back_button(message):
    try:
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton("Назад", callback_data="back_to_menu")
        markup.add(back)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
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
        bot.send_message(message.chat.id, f"Ваш возраст: {age}. Теперь напишите ваше имя:")
        bot.register_next_step_handler(message, get_name)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный возраст (число):")
        bot.register_next_step_handler(message, get_age)
    except Exception as e:
        print(f"Ошибка в get_age: {e}")

def get_name(message):
    try:
        name = message.text
        bot.send_message(message.chat.id, f"Спасибо, {name}! Пожалуйста, поделитесь своим Telegram-контактом:", reply_markup=contact_share_markup())
    except Exception as e:
        print(f"Ошибка в get_name: {e}")

# Кнопка для отправки контакта
def contact_share_markup():
    try:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        contact_button = types.KeyboardButton("Поделиться контактом", request_contact=True)
        markup.add(contact_button)
        return markup
    except Exception as e:
        print(f"Ошибка в contact_share_markup: {e}")

# Обработка контактов
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        if message.contact:
            # Форматирование текста с HTML
            contact_info = (
                "<b>🚨 Новый контакт! 🚨</b>\n"
                "<b>📱 Имя:</b> {0}\n"
                "<b>📞 Телефон:</b> {1}\n".format(message.contact.first_name, message.contact.phone_number)
            )
            # Отправляем админу
            bot.send_message('677342937', contact_info, parse_mode='HTML')
            # Подтверждение пользователю
            bot.send_message(message.chat.id, "Спасибо! Ваш контакт успешно отправлен.")
            # Удаляем кнопку "Поделиться контактом"
            bot.delete_message(message.chat.id, message.message_id)
            # Убираем старую клавиатуру
            markup = types.ReplyKeyboardRemove()  # Убираем старую клавиатуру
            bot.send_message(message.chat.id, "Теперь можете выбрать одно из действий:", reply_markup=markup)

            # Возврат в основное меню
            show_tasks_panel(message)
    except Exception as e:
        print(f"Ошибка в handle_contact: {e}")

# Функция для запуска бота в фоновом режиме
def run_bot():
    bot.polling(non_stop=True)

# Запуск бота в отдельном потоке
if __name__ == '__main__':
    # Запускаем Telegram-бота в отдельном потоке
    t = Thread(target=run_bot)
    t.start()

    # Запуск Flask-приложения
    app.run(host='0.0.0.0', port=5000)
