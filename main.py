# -*- coding: utf-8 -*-
from bot_commands.profile import *
from bot_commands.budget import *
from bot_commands.projects import *
from bot_commands.marks import *
from bot_commands.inviting import *
from bot_commands.tokens import *
from bot_commands.votings import *
from config import bot, db, cursor, get_keyboard, isRang
from emoji import emojize
import cherrypy
import webhook


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        username = "@" + message.from_user.username
        if IsAbit(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Привет! Я бот антишколы Корпус, мне сказали что ты наш новый курсант, давай я занесу твои данные в базу. Начнём с имени, как тебя зовут?")
            SetState(username, 1, cursor, db)
        elif IsInvitedInvestor(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Здравствуйте, я ваш личный помощник, бот анти-школы Корпус. Я буду помогать взаимодействать с нашей системой. Давайте для начала внесём ваши данные в нашу базу. Начнём с имени. Напишите ваше полное имя")
            SetState(username, 1, cursor, db)
        elif IsInvitedTutor(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Добрый день. Вы назначены тьютором анти-школы Корпус. Давайте для начала внесём ваши данные в нашу базу. Начнём с имени. Напишите ваше полное имя")
            SetState(username, 1, cursor, db)
        elif IsInvitedExpert(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Добрый день, уважаемый эксперт. Вы стали частью нашего коммьюнити. Давайте для начала внесём ваши данные в нашу базу. Начнём с имени. Напишите ваше полное имя")
            SetState(username, 1, cursor, db)
        elif IsInvitedEducator(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Добрый день. Вы назначены преподавателем анти-школы Корпус. Давайте для начала внесём ваши данные в нашу базу. Начнём с имени. Напишите ваше полное имя")
            SetState(username, 1, cursor, db)
        elif not (IsUserInDB(username, cursor, db)):
            keyboard = telebot.types.InlineKeyboardMarkup()
            url_button = telebot.types.InlineKeyboardButton(text="Наш канал",
                                                            url="https://t.me/joinchat/FcADIxGou--U0fMfLs9Tvg")
            keyboard.add(url_button)
            bot.send_message(message.chat.id,
                             "Привет. Сейчас я отправлю тебе ссылку на наш канал. Если ты хочешь стать частью нашего комьюнити - напиши туда и тебе обязательно ответят.",
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Главное меню',
                             reply_markup=get_keyboard('@' + message.from_user.username))


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 0)
def user_start(message):
    start(message)


@bot.message_handler(content_types=["text"])
def text(message):
    if not (IsUserInDB('@' + message.from_user.username, cursor, db)):
        keyboard = telebot.types.InlineKeyboardMarkup()
        url_button = telebot.types.InlineKeyboardButton(text="Наш канал",
                                                        url="https://t.me/joinchat/FcADIxGou--U0fMfLs9Tvg")
        keyboard.add(url_button)
        bot.send_message(message.chat.id,
                         "Привет. Сейчас я отправлю тебе ссылку на наш канал. Если ты хочешь стать частью нашего комьюнити - напиши туда и тебе обязательно ответят.",
                         reply_markup=keyboard)
    elif message.chat.type == 'private':
        mess = message.text
        print(message.text)
        cherrypy.log(message.text)
        if mess == '📂 Проекты':
            projectsMenu(message)
        elif mess == '📊 Оценки':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            if IsUserTeamlead('@'+message.from_user.username,cursor):
                keyboard.add(emojize(':crown: Оценка нематериального вклада'))
            if isRang(GetRangs('@' + message.from_user.username, cursor), [2, 3, 4]):
                keyboard.add(emojize(':eyes: Посмотреть свои оценки'))
            if isRang(GetRangs('@' + message.from_user.username, cursor), [5, 8, 9, 10]):
                keyboard.add(emojize(':newspaper: Оценки пользователей'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Оценки"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '👑 Оценка нематериального вклада':
            pass
        elif mess == '👀 Посмотреть свои оценки':
            marks(message)
        elif mess == '📋 Профиль':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row(emojize(':eyes: Посмотреть профиль'),
                         emojize(':scissors: Редактировать профиль'),
                         emojize(':name_badge: Сбросить профиль'))
            if isRang(GetRangs('@' + message.from_user.username, cursor), [5, 8, 9, 10]):
                keyboard.add(emojize(':newspaper: Профили пользователей'))
            keyboard.add(emojize('Назад'))
            bot.send_message(message.chat.id, 'Вкладка <b>"Профиль"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '➕📓 Добавить абитуриентов':
            add_abit(message)
        elif mess == '👔 Функции администратора':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.add('Добавить пользователей в систему')
            keyboard.row('Указать роль для пользователя', 'Убрать роль пользователя')
            # if IsThereActiveVoting(cursor):
            #     keyboard.add('Закончить утверждение бюджета')
            # else:
            #     keyboard.add(emojize(':loudspeaker: Начать голосование за утверждение бюджета'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Администратор"</b>', reply_markup=keyboard,
                             parse_mode='HTML')
        elif mess == 'Указать роль для пользователя':
            set_rang(message)
        elif mess == 'Убрать роль пользователя':
            delete_rang(message)
        elif mess == 'Добавить пользователей в систему':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row(emojize(':heavy_plus_sign::notebook: Добавить абитуриентов'),
                         emojize(':heavy_plus_sign::money_with_wings: Добавить инвесторов'))
            keyboard.row(emojize(':heavy_plus_sign::trophy: Добавить тьюторов'),
                         emojize(':heavy_plus_sign::microscope: Добавить экспертов'))
            keyboard.add(emojize(':heavy_plus_sign::pencil: Добавить преподавателей'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Кого вы хотите добавить?', reply_markup=keyboard)
        elif mess == '➕🏆 Добавить тьюторов':
            add_tutor(message)
        elif mess == '➕🔬 Добавить экспертов':
            add_expert(message)
        elif mess == '➕✏ Добавить преподавателей':
            add_educator(message)
        elif mess == '💳 Функции инвестора':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row('Купить токены у пользователей', 'Продать токены пользователям')
            keyboard.row('Купить токены у системы', 'Продать токены системе')
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Инвестор"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '👀 Посмотреть профиль':
            get_profile(message)
        elif mess == '✂ Редактировать профиль':
            red_profile(message)
        elif mess == '📛 Сбросить профиль':
            reset(message)
        elif mess == '➕💸 Добавить инвесторов':
            add_investor(message)
        elif mess == '📰 Профили пользователей':
            look_profiles(message)
        elif mess == '📰 Оценки пользователей':
            look_marks(message)
        elif mess == "Создать новый проект":
            project_switch(message, 1)
        elif mess == "Редактировать проект":
            project_switch(message, 2)
        elif mess == "Список проектов":
            project_switch(message, 3)
        elif mess == 'Назад':
            bot.send_message(message.chat.id, 'Главное меню',
                             reply_markup=get_keyboard('@' + message.from_user.username))
        elif mess == '📢 Начать голосование за утверждение бюджета':
            send_budget_offer(message)
        elif mess == 'Закончить утверждение бюджета':
            finish_budget(message)
        elif mess == 'Функции тьютора':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.add(emojize(':heavy_plus_sign::notebook: Добавить абитуриентов'))
            keyboard.row('Добавить досье пользователю', 'Посмотреть досье пользователя')
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Тьютор"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == 'Добавить досье пользователю':
            add_dosier(message)
        elif mess == 'Посмотреть досье пользователя':
            look_dosier(message)
        elif mess == '🌐 Токены' or mess == 'Вернуться':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.add(emojize(':performing_arts: Обменяться токенами вклада'))
            keyboard.add(emojize(':currency_exchange: Обменять токены инвестиции на токены вклада'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Работа с токенами Корпуса', reply_markup=keyboard)
        elif mess == '🎭 Обменяться токенами вклада':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row('Попросить токены вклада', 'Передать токены вклада')
            keyboard.add('Вернуться')
            bot.send_message(message.chat.id, 'Что вы хотите?', reply_markup=keyboard)
        elif mess == 'Попросить токены вклада':
            ask_tokens(message)
        elif mess == 'Передать токены вклада':
            give_tokens(message)
        elif mess == '💱 Обменять токены инвестиции на токены вклада':
            change_investment_tokens(message)
        elif mess in ['hi', 'Hi', 'Привет', 'привет', 'hello', 'Hello']:
            bot.send_message(message.chat.id, 'Привет, ' + '@' + message.from_user.username,
                             reply_markup=get_keyboard('@' + message.from_user.username))
        elif mess in ['Купить токены у пользователей', 'Продать токены пользователям', 'Купить токены у системы',
                      'Продать токены системе']:
            bot.send_message(message.chat.id, 'Функция пока недоступна',
                             reply_markup=get_keyboard('@' + message.from_user.username))
        else:
            bot.send_message(message.chat.id, 'Неизвестная команда',
                             reply_markup=get_keyboard('@' + message.from_user.username))

# import logging
#
# logging.basicConfig(filename="log.log", level=logging.INFO)
# try:
#     now_date = datetime.datetime.today()
#     now_date = now_date.strftime("%d/%m/%y %H:%M")
#     logging.info('['+now_date+'] Bot started')
#     bot.remove_webhook()
#     bot.set_webhook(url=webhook.WEBHOOK_URL_BASE + webhook.WEBHOOK_URL_PATH,certificate=open(webhook.WEBHOOK_SSL_CERT, 'r'))
#     cherrypy.config.update({
#             'server.socket_host': webhook.WEBHOOK_LISTEN,
#             'server.socket_port': webhook.WEBHOOK_PORT,
#             'server.ssl_module': 'builtin',
#             'server.ssl_certificate': webhook.WEBHOOK_SSL_CERT,
#             'server.ssl_private_key': webhook.WEBHOOK_SSL_PRIV
#         })
#     cherrypy.quickstart(webhook.WebhookServer(), webhook.WEBHOOK_URL_PATH, {'/': {}})
# except:
#     now_date = datetime.datetime.today()
#     now_date = now_date.strftime("%d/%m/%y %H:%M")
#     logging.debug('[' + now_date + '] Bot dropped')
#
# now_date = datetime.datetime.today()
# now_date = now_date.strftime("%d/%m/%y %H:%M")
# logging.info('['+now_date+'] Bot finished')

bot.polling(none_stop=True)

