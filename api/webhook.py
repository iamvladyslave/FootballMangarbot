from flask import Flask, request, jsonify
import telebot
from telebot import types
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация Flask приложения
app = Flask(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные (в продакшене лучше использовать Redis или базу данных)
sent_messages = {}
user_data = {}
ADMIN_USERNAME = '@matagency_official'
ADMIN_ID = None

# Функция для получения ID админа
def get_admin_id():
    global ADMIN_ID
    if ADMIN_ID is not None:
        return ADMIN_ID
    try:
        user = bot.get_chat(ADMIN_USERNAME)
        ADMIN_ID = user.id
        return ADMIN_ID
    except Exception as e:
        logger.error(f"Ошибка получения ID админа: {e}")
        return None

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
                try:
                    bot.delete_message(chat_id, message_id)
                except Exception:
                    pass
            sent_messages[chat_id] = []
    except Exception as e:
        logger.error(f"Ошибка удаления сообщений: {e}")

# Тексты (можно вынести в отдельный файл)
about_me_text = (
    "👋 Привет! Я футбольный менеджер с многолетним опытом работы.\n\n"
    "⚽ Моя специализация:\n"
    "• Поиск и подбор талантливых игроков\n"
    "• Переговоры с клубами\n"
    "• Контрактное право в футболе\n"
    "• Карьерное планирование\n\n"
    "📈 Статистика:\n"
    "• Более 50 успешных трансферов\n"
    "• Работа с топ-клубами Европы\n"
    "• 95% довольных клиентов\n\n"
    "💼 Готов помочь вам построить успешную карьеру в футболе!"
)

pricing_text = (
    "💰 РАСЦЕНКИ НА УСЛУГИ\n\n"
    "🔍 Поиск и подбор игроков:\n"
    "• Анализ рынка: 500€\n"
    "• Поиск талантов: 1000€\n"
    "• Полный скрининг: 2000€\n\n"
    "📋 Консультации:\n"
    "• Разовая консультация: 200€\n"
    "• Пакет консультаций (5 сессий): 800€\n"
    "• Годовое сопровождение: 5000€\n\n"
    "📄 Документооборот:\n"
    "• Составление контракта: 300€\n"
    "• Переговоры с клубом: 1000€\n"
    "• Полное сопровождение сделки: 2000€\n\n"
    "💡 Все цены указаны без учета налогов"
)

terms_text = (
    "📋 УСЛОВИЯ РАБОТЫ\n\n"
    "⏰ Сроки выполнения:\n"
    "• Консультации: в течение 24 часов\n"
    "• Поиск игроков: 2-4 недели\n"
    "• Переговоры: 1-2 недели\n\n"
    "💳 Оплата:\n"
    "• Предоплата 50% при заключении договора\n"
    "• Остальные 50% по завершении работы\n"
    "• Возможна рассрочка для крупных проектов\n\n"
    "🔄 Гарантии:\n"
    "• Полный возврат средств при невыполнении условий\n"
    "• Бесплатные корректировки в течение 30 дней\n"
    "• Конфиденциальность всех данных\n\n"
    "📞 Связь:\n"
    "• Ответ в течение 2 часов в рабочее время\n"
    "• Поддержка 24/7 для срочных вопросов"
)

# Обработчики команд
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id == get_admin_id():
        show_tasks_panel_admin(message)
    else:
        show_main_menu(message)

@bot.message_handler(commands=['menu'])
def handle_menu(message):
    show_tasks_panel(message)

@bot.message_handler(commands=['tasks'])
def handle_tasks(message):
    show_tasks_panel(message)

@bot.message_handler(commands=['pricing'])
def handle_pricing(message):
    delete_previous_messages(message.chat.id)
    bot.send_message(message.chat.id, pricing_text)
    show_back_button(message.chat.id)

@bot.message_handler(commands=['terms'])
def handle_terms(message):
    delete_previous_messages(message.chat.id)
    bot.send_message(message.chat.id, terms_text)
    show_back_button(message.chat.id)

@bot.message_handler(commands=['contact'])
def handle_contact(message):
    delete_previous_messages(message.chat.id)
    bot.send_message(message.chat.id, "Для связи со мной, пожалуйста, заполните анкету:")
    bot.send_message(message.chat.id, "Сколько вам лет?")
    bot.register_next_step_handler(message, get_age)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "about_me":
            # Отправляем текст "Обо мне"
            bot.send_message(call.message.chat.id, about_me_text)
            
            # Панель с кнопками
            panel = types.InlineKeyboardMarkup(row_width=2)
            panel.add(
                types.InlineKeyboardButton("Расценки💸", callback_data="pricing"),
                types.InlineKeyboardButton("Условия работы👨‍💻", callback_data="terms"),
                types.InlineKeyboardButton("Связаться со мной📞", callback_data="contact")
            )
            bot.send_message(call.message.chat.id, "Выберите действие ниже:", reply_markup=panel)
            
        elif call.data == "pricing":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, pricing_text)
            show_back_button(call.message.chat.id)
            
        elif call.data == "terms":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, terms_text)
            show_back_button(call.message.chat.id)
            
        elif call.data == "contact":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "Для связи со мной, пожалуйста, заполните анкету:")
            bot.send_message(call.message.chat.id, "Сколько вам лет?")
            bot.register_next_step_handler(call.message, get_age)
            
        elif call.data == "back_to_menu":
            show_tasks_panel(call.message)
            
        # Админские функции
        elif call.data == "edit1":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "👨 Пожалуйста, введите новый текст для раздела 'Обо мне':")
            bot.register_next_step_handler(call.message, update_about_me_text)
            
        elif call.data == "edit2":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "👨 Пожалуйста, загрузите новое фото для добавления в галерею.")
            bot.register_next_step_handler(call.message, receive_new_photo)
            
        elif call.data == "edit3":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "👨 Пожалуйста, введите новые расценки:")
            bot.register_next_step_handler(call.message, update_pricing)
            
        elif call.data == "edit4":
            delete_previous_messages(call.message.chat.id)
            bot.send_message(call.message.chat.id, "👨 Пожалуйста, введите новые условия работы:")
            bot.register_next_step_handler(call.message, update_terms)
            
    except Exception as e:
        logger.error(f"Ошибка в обработке callback: {e}")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text.lower() not in ['/start', '/menu', '/tasks', '/pricing', '/terms', '/contact']:
        show_tasks_panel(message)

# Функции для отображения меню
def show_main_menu(message):
    delete_previous_messages(message.chat.id)
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
    msg = bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    save_sent_message(message.chat.id, msg.message_id)

def show_tasks_panel(message):
    try:
        delete_previous_messages(message.chat.id)
        task_text = "Выберите действие ниже:"
        panel = types.InlineKeyboardMarkup(row_width=2)
        panel.add(
            types.InlineKeyboardButton("Расценки💸", callback_data="pricing"),
            types.InlineKeyboardButton("Условия работы👨‍💻", callback_data="terms"),
            types.InlineKeyboardButton("Связаться со мной📞", callback_data="contact")
        )
        msg = bot.send_message(message.chat.id, task_text, reply_markup=panel)
        save_sent_message(message.chat.id, msg.message_id)
    except Exception as e:
        logger.error(f"Ошибка в show_tasks_panel: {e}")

def show_tasks_panel_admin(message):
    try:
        delete_previous_messages(message.chat.id)
        task_text = "👨‍💼 Панель администратора. Выберите действие:"
        panel = types.InlineKeyboardMarkup(row_width=2)
        panel.add(
            types.InlineKeyboardButton("Изменить 'Обо мне'", callback_data="edit1"),
            types.InlineKeyboardButton("Добавить фото", callback_data="edit2"),
            types.InlineKeyboardButton("Изменить расценки", callback_data="edit3"),
            types.InlineKeyboardButton("Изменить условия", callback_data="edit4"),
        )
        msg = bot.send_message(message.chat.id, task_text, reply_markup=panel)
        save_sent_message(message.chat.id, msg.message_id)
    except Exception as e:
        logger.error(f"Ошибка в show_tasks_panel_admin: {e}")

def show_back_button(chat_id):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_menu")
    markup.add(back_button)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Функции для обработки анкеты
def get_age(message):
    try:
        if message.text.startswith('/'):
            show_tasks_panel(message)
            return
        age = int(message.text)
        if age < 10 or age > 100:
            bot.send_message(message.chat.id, "Пожалуйста, введите реальный возраст (от 10 до 100):")
            bot.register_next_step_handler(message, get_age)
            return
        user_data[message.chat.id] = {'age': age}
        bot.send_message(message.chat.id, f"Ваш возраст: {age}. Теперь напишите ваше имя:")
        bot.register_next_step_handler(message, get_name)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный возраст (число):")
        bot.register_next_step_handler(message, get_age)
    except Exception as e:
        logger.error(f"Ошибка в get_age: {e}")

def get_name(message):
    try:
        if message.text.startswith('/'):
            show_tasks_panel(message)
            return
        name = message.text
        if len(name) < 2 or len(name) > 30:
            bot.send_message(message.chat.id, "Имя должно быть от 2 до 30 символов. Введите снова:")
            bot.register_next_step_handler(message, get_name)
            return
        user_data[message.chat.id]['name'] = name
        bot.send_message(message.chat.id, f"Спасибо, {name}! Пожалуйста, поделитесь своим Telegram-контактом:", reply_markup=contact_share_markup())
    except Exception as e:
        logger.error(f"Ошибка в get_name: {e}")

def contact_share_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_button = types.KeyboardButton("📞 Поделиться контактом", request_contact=True)
    markup.add(contact_button)
    return markup

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        if message.chat.id in user_data:
            contact_info = (
                f"📞 <b>Новый контакт!</b>\n\n"
                f"👤 Имя: {user_data[message.chat.id].get('name', 'Не указано')}\n"
                f"🎂 Возраст: {user_data[message.chat.id].get('age', 'Не указан')}\n"
                f"📱 Телефон: {message.contact.phone_number}\n"
                f"👤 Username: @{message.from_user.username if message.from_user.username else 'Не указан'}\n"
                f"🆔 ID: {message.from_user.id}"
            )
            # Отправляем админу
            bot.send_message(get_admin_id(), contact_info, parse_mode='HTML')
            
            # Подтверждение пользователю
            bot.send_message(message.chat.id, "✅ Спасибо! Ваш контакт отправлен. Я свяжусь с вами в ближайшее время.")
            show_tasks_panel(message)
        else:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
            show_tasks_panel(message)
    except Exception as e:
        logger.error(f"Ошибка в handle_contact: {e}")

# Функции для админа
def update_about_me_text(message):
    try:
        global about_me_text
        about_me_text = message.text
        bot.send_message(message.chat.id, "✅ Текст 'Обо мне' успешно обновлен!")
        show_tasks_panel_admin(message)
    except Exception as e:
        logger.error(f"Ошибка в update_about_me_text: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_about_me_text)

def update_pricing(message):
    try:
        global pricing_text
        pricing_text = message.text
        bot.send_message(message.chat.id, "✅ Расценки успешно обновлены!")
        show_tasks_panel_admin(message)
    except Exception as e:
        logger.error(f"Ошибка в update_pricing: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_pricing)

def update_terms(message):
    try:
        global terms_text
        terms_text = message.text
        bot.send_message(message.chat.id, "✅ Условия работы успешно обновлены!")
        show_tasks_panel_admin(message)
    except Exception as e:
        logger.error(f"Ошибка в update_terms: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обновлении текста. Попробуйте еще раз.")
        bot.register_next_step_handler(message, update_terms)

def receive_new_photo(message):
    try:
        if message.content_type == 'photo':
            # В Vercel мы не можем сохранять файлы локально
            # Вместо этого отправляем админу информацию о фото
            bot.send_message(message.chat.id, "✅ Фото получено! В Vercel фото сохраняются в облаке.")
            show_tasks_panel_admin(message)
        else:
            bot.send_message(message.chat.id, "⚠️ Пожалуйста, отправьте изображение.")
            bot.register_next_step_handler(message, receive_new_photo)
    except Exception as e:
        logger.error(f"Ошибка в receive_new_photo: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке фото. Попробуйте еще раз.")
        bot.register_next_step_handler(message, receive_new_photo)

# Webhook endpoint для Vercel
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'
    else:
        return 'Bad Request', 400

# Главная страница (для проверки работы)
@app.route('/')
def index():
    return 'Telegram Bot is running!'

# Обработчик для Vercel
@app.route('/api/webhook', methods=['POST'])
def api_webhook():
    return webhook()

if __name__ == '__main__':
    app.run(debug=True)
