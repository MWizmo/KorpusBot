# -*- coding: utf-8 -*-
import telebot
from db_commands import *
import sqlite3
import config
from emoji import emojize
import mysql.connector
import cherrypy

WEBHOOK_HOST = '195.201.138.7'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '195.201.138.7'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)
db = sqlite3.connect("korpus.db", check_same_thread=False)
#db = mysql.connector.connect('localhost', 'root', '', 'Korpus')
cursor = db.cursor()
user_info = dict()

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

def get_keyboard(rang, second_rang):
    rang = int(rang)
    second_rang = int(second_rang)
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(emojize(":bar_chart: Оценки", use_aliases=True),
               emojize(':open_file_folder: Проекты', use_aliases=True),
               emojize(':clipboard: Профиль', use_aliases=True))
    if rang == 5 or second_rang == 5:
        markup.add(emojize(':heavy_plus_sign::notebook: Добавить абитуриентов'))
    elif rang == 9 or second_rang == 9:
        markup.add(emojize(':necktie: Функции администратора'))
    if rang == 8 or second_rang == 8:
        markup.row(emojize(':credit_card: Функции инвестора'))
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        username = "@" + message.from_user.username
        if IsAbit(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Привет! Я бот антишколы Корпус, мне сказали что ты наш новый курсант, давай я занесу твои данные в базу. \
                             Начнём с имени, как тебя зовут?")
            SetState(username, 1, cursor, db)
        elif IsInvitedInvestor(username, cursor, db):
            bot.send_message(message.chat.id,
                             "Привет! Я бот антишколы Корпус, давай я занесу данные о нашем новом инвесторе в базу. \
                             Начнём с имени, как тебя зовут?")
            SetState(username, 1, cursor, db)

        elif not(IsUserInDB(username, cursor, db)):
            keyboard = telebot.types.InlineKeyboardMarkup()
            url_button = telebot.types.InlineKeyboardButton(text="Наш канал",
                                                            url="https://t.me/joinchat/FcADIxGou--U0fMfLs9Tvg")
            keyboard.add(url_button)
            bot.send_message(message.chat.id,
                             "Прости, тебя нет в нашей базе. Но заходи на наш канал. Может, скоро увидимся",
                             reply_markup=keyboard)


@bot.message_handler(commands=['add_abit'])
def add_abit(message):
    if message.chat.type == 'private':
        if GetRang(message.from_user.username, cursor) in [5, 7, 9] or GetSecondRang(message.from_user.username, cursor) in [5, 7, 9]:
            keyboard=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id, 'Введите никнеймы абитуриентов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 8, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 8)
def adding_abit(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все абитуриенты успешно зачислены',
                         reply_markup=get_keyboard(GetRang('@'+message.from_user.username, cursor),
                                                   GetSecondRang('@'+message.from_user.username, cursor)))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not(IsUserInDB(nick, cursor, db)):
            AddAbit(nick, cursor, db)
            bot.send_message(message.chat.id, "Абитуриент зачислен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(commands=['invite_investor'])
def add_investor(message):
    if message.chat.type == 'private':
        if GetRang(message.from_user.username, cursor) in[9] or GetSecondRang(message.from_user.username, cursor) in[9]:
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id, 'Введите никнеймы инвесторов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 81, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 81)
def adding_investor(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все инвесторы успешно добавлены',
                         reply_markup=get_keyboard(GetRang('@'+message.from_user.username, cursor),
                                                   GetSecondRang('@'+message.from_user.username, cursor)))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not(IsUserInDB(nick, cursor, db)):
            InviteInvestor(nick, cursor, db)
            bot.send_message(message.chat.id, "Инвестор добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 0)
def user_start(message):
    username = "@"+message.from_user.username
    if IsAbit(username, cursor, db):
        bot.send_message(message.chat.id, "Привет! Я бот антишколы Корпус, мне сказали, что ты наш новый курсант,\
                                            давай я занесу твои данные в базу. Начнём с имени, как тебя зовут?")
        SetState(username, 1, cursor, db)
    elif IsInvitedInvestor(username, cursor, db):
        bot.send_message(message.chat.id, "Привет! Я бот антишколы Корпус, давай я занесу данные о нашем новом инвесторе\
                                                в базу. Начнём с имени, как тебя зовут?")
        SetState(username, 1, cursor, db)
    else:
        bot.send_message(message.chat.id, "А ты кто такой?")


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 1)
def user_entering_fio(message):
    user_info['name'] = message.text
    bot.send_message(message.chat.id, "Всё, кажется запомнил. Теперь напиши свой номер телефона, он мне пригодится")
    SetState("@" + message.from_user.username, 2, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 2)
def user_entering_phone(message):
    user_info['phone'] = message.text
    bot.send_message(message.chat.id, "Номер есть, тепeрь дай мне адрес электронной почты")
    SetState("@" + message.from_user.username, 3, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 3)
def user_entering_email(message):
    user_info['email'] = message.text
    bot.send_message(message.chat.id, "Принял, теперь мне нужная твоя фотография, только давай без приколов")
    SetState("@" + message.from_user.username, 4, cursor, db)


@bot.message_handler(content_types=["photo"],
                     func=lambda message: GetState(message.from_user.username, cursor, db) == 4)
def user_entering_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    username = "@" + message.from_user.username
    if IsAbit(username, cursor, db):
        UpgradeTo1(username, user_info['name'], photo, user_info['phone'], user_info['email'], cursor, db)
        SetChatId('@' + message.from_user.username, message.chat.id, cursor, db)
        bot.send_message(message.chat.id, "Красавчик, спасибо. Отныне ты курсант антишколы Корпус!",
                         reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                   GetSecondRang('@' + message.from_user.username, cursor)))
    elif IsInvitedInvestor(username, cursor, db):
        BecomeInvestor(username, user_info['name'], photo, user_info['phone'], user_info['email'], cursor, db)
        SetChatId('@' + message.from_user.username, message.chat.id, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь ты полноправный инвестор!",
                         reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                   GetSecondRang('@' + message.from_user.username, cursor)))
    else:
        UpdateProfile(username, user_info['name'], photo, user_info['phone'], user_info['email'], cursor, db)
        bot.send_message(message.chat.id, "Профиль обновлен",
                         reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                   GetSecondRang('@' + message.from_user.username, cursor)))
    SetState("@" + message.from_user.username, 6, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 4)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(commands=["reset_profile"])
def reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    SetState("@" + message.from_user.username, 1, cursor, db)


@bot.message_handler(commands=["red_profile"])
def red_profile(message):
    keyboard=telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Имя',callback_data='profile_1'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Телефон', callback_data='profile_2'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Электронный адрес', callback_data='profile_3'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Фото', callback_data='profile_4'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='profile_5'))
    bot.send_message(message.chat.id,'Что вы хотите изменить?',reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('profile'))
def redacting_profile(call):
    if call.data[-1]=='1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Введите новое имя')
        SetState('@'+call.from_user.username,41,cursor,db)
    if call.data[-1]=='2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Введите новый телефон')
        SetState('@'+call.from_user.username,42,cursor,db)
    if call.data[-1]=='3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Введите новый электронный адрес')
        SetState('@'+call.from_user.username,43,cursor,db)
    if call.data[-1]=='4':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Загрузите новое фото')
        SetState('@'+call.from_user.username,44,cursor,db)
    if call.data[-1]=='5':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,'Редактирование окончено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))
        SetState('@'+call.from_user.username,6,cursor,db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 41)
def user_redacting_fio(message):
    name = message.text
    UpdateName("@" + message.from_user.username, name, cursor, db)
    bot.send_message(message.chat.id, text='Имя изменено')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 42)
def user_redacting_phone(message):
    phone = message.text
    UpdatePhone("@" + message.from_user.username, phone, cursor, db)
    bot.send_message(message.chat.id, text='Телефон изменен')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 43)
def user_redacting_email(message):
    email = message.text
    UpdateEmail("@" + message.from_user.username, email, cursor, db)
    bot.send_message(message.chat.id, text='Электронный адрес изменен')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)


@bot.message_handler(content_types=["photo"],func=lambda message: GetState(message.from_user.username, cursor, db) == 44)
def user_redacting_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    UpdatePhoto("@" + message.from_user.username, photo, cursor, db)
    bot.send_message(message.chat.id, text='Фото изменено')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 44)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(commands=["profile"])
def get_profile(message):
    if message.chat.type == 'private':
        if GetRang(message.from_user.username, cursor) in range(2, 10):
            profile = GetProfile('@'+message.from_user.username, cursor)
            if profile[0] != None:
                string = 'Курсант: ' + profile[0]
                string += "\nФото: "
                bot.send_message(message.chat.id, string)
                try:
                    bot.send_photo(message.chat.id, profile[3])
                except telebot.apihelper.ApiException:
                    bot.send_message(message.chat.id, 'Фото недоступно')
                string = "Телефон: " + str(profile[1])
                string = string + "\nЭлектронная почта: " + profile[2]
                string = string + "\nДата регистрации: " + profile[6]
                string = string + '\nАвторитет: ' + str(profile[4])
                string = string + '\nБаланс: ' + str(profile[5])
                if profile[7] == None:
                    string = string + '\nСумма оценок в текущем месяце: 0'
                else:
                    string = string + '\nСумма оценок в текущем месяце: ' + str(profile[7])
                if profile[8] != None:
                    string = string + '\nДосье: ' + profile[8]
                bot.send_message(message.chat.id, string,
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
            else:
                bot.send_message(message.chat.id, "Ой, анкета еще не заполнена",
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
            SetState("@" + message.from_user.username, 6, cursor, db)

@bot.message_handler(commands=["list"])
def users_list(message):
    if(message.chat.type=='private'):
        if (GetRang(message.from_user.username, cursor) in range(2,10)):
            list=GetListOfUsers(cursor)
            for user in list:
                string=''
                if user[5]!=None:
                    string =string + 'Пользователь: ' + user[5] + ' (' + user[0] + ')     Ранг: ' + GetTitleOfRang(user[1],cursor)
                else:
                    string = string + 'Пользователь: ' +  user[0] + '     Ранг: ' + GetTitleOfRang(user[1], cursor)
                if(user[2]!=None):
                    string+='    Доп. ранг: '+GetTitleOfRang(user[2],cursor)
                #if (user[4] != None):
                 #   string += '    Сумма оценок: ' + GetTitleOfRang(user[4], cursor)
                bot.send_message(message.chat.id,string,reply_markup=get_keyboard(GetRang('@'+message.from_user.username,cursor),GetSecondRang('@'+message.from_user.username,cursor)))

@bot.message_handler(commands=["projects"])
def projectsMenu(message):
    if(message.chat.type=='private'):
        # keyboard = telebot.types.InlineKeyboardMarkup()
        # new_project = telebot.types.InlineKeyboardButton(text="Создать новый проект", callback_data='projects_1')
        # edit_project=telebot.types.InlineKeyboardButton(text="Редактировать проект", callback_data='projects_2')
        # list_project=telebot.types.InlineKeyboardButton(text="Список проектов", callback_data='projects_3')
        # exit=telebot.types.InlineKeyboardButton(text="Выход", callback_data='projects_4')
        keyboard=telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project="Редактировать проект"
        list_project="Список проектов"
        exit="Назад"
        flag=True
        if(GetRang('@'+message.from_user.username,cursor) in [9,10] or GetSecondRang('@'+message.from_user.username,cursor) in [9,10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag=False
        if(IsUserTeamlead('@'+message.from_user.username,cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard,parse_mode='HTML')


def project_switch(message,flag):
    #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Вкладка <b>"Проекты"</b>',parse_mode='HTML')
    if flag==1:
        bot.send_message(message.chat.id, 'Введите название проекта')
        SetState("@" + message.from_user.username, 21, cursor, db)
    elif flag==2:
        projects=GetProjects("@" + message.from_user.username,cursor)
        keyboard=telebot.types.InlineKeyboardMarkup()
        for i in range(0,len(projects)):
            keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],callback_data='edit_project_'+str(projects[i][1])))
        bot.send_message(message.chat.id,'Доступные для редактирования проекты',reply_markup=keyboard)
    elif flag==3:
        projects = GetAllProjects(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(0, len(projects)):
            keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],
                                                            callback_data='look_project_' + projects[i][0]))
        bot.send_message(message.chat.id, 'Все проекты "Корпуса"', reply_markup=keyboard)
    elif flag==4:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        bot.send_message(message.chat.id,'Работа с проектами завершена',reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                    GetSecondRang('@' + message.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_project'))
def look_project(call):
    title=call.data[13:]
    id=GetProject(title,cursor)
    info=GetProjectInfo(id,cursor)
    bot.send_message(call.message.chat.id,info,parse_mode='HTML')
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    new_project = "Создать новый проект"
    edit_project = "Редактировать проект"
    list_project = "Список проектов"
    exit = "Назад"
    flag = True
    if (GetRang('@' + call.from_user.username, cursor) in [9, 10] or GetSecondRang('@' + call.from_user.username,
                                                                                      cursor) in [9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
        keyboard.add(edit_project)
    keyboard.add(list_project)
    keyboard.add(exit)
    bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard,parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('edit_project'))
def edit_project(call):
    id=call.data[13:]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Доступные для редактирования проекты")
    info = GetProjectInfo(id, cursor)
    bot.send_message(call.message.chat.id, info, parse_mode='HTML')
    keyboard=telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Добавить участника', callback_data='editing_project_1'+str(id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Удалить участника', callback_data='editing_project_2' + str(id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Изменить статус проекта', callback_data='editing_project_3' + str(id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Выход', callback_data='editing_project_4' + str(id)))
    bot.send_message(call.message.chat.id,'Что вы хотите сделать?',reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('editing_project'))
def editing(call):
    id=call.data[17:]
    SetCurrProject(id,'@'+call.from_user.username,cursor,db)
    num=call.data[16]
    if num=='1':
        keyboard=telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('Закончить')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите никнеймы курсантов, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                         reply_markup=keyboard)
        username = "@" + call.from_user.username
        SetState(username, 22, cursor, db)
    elif num=='2':
        members=GetMembersOfProject(id,cursor)
        keyboard=telebot.types.InlineKeyboardMarkup()
        for member in members:
            keyboard.add(telebot.types.InlineKeyboardButton(text=member[0],callback_data='delete_'+member[0]+'*'+str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить',callback_data='delete_%'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Выберите курсанта из списка участников',reply_markup=keyboard)
    elif num=='3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Введите новый статус проекта')
        SetCurrProject(id,'@'+call.from_user.username,cursor,db)
        SetState('@'+call.from_user.username, 23, cursor, db)
    elif num=='4':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if (GetRang('@' + call.from_user.username, cursor) in [9, 10] or GetSecondRang(
                '@' + call.from_user.username, cursor) in [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.edit_message_text(call.message.chat.id,'Вкладка <b>"Проекты"</b>', reply_markup=keyboard,parse_mode='HTML')

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 23)
def edit_status(message):
    status=message.text
    ChangeStatusProject(status,GetCurrProject('@'+message.from_user.username,cursor),cursor,db)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    new_project = "Создать новый проект"
    edit_project = "Редактировать проект"
    list_project = "Список проектов"
    exit = "Назад"
    flag = True
    if (GetRang('@' + message.from_user.username, cursor) in [9, 10] or GetSecondRang(
            '@' + message.from_user.username, cursor) in [9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
        keyboard.add(edit_project)
    keyboard.add(list_project)
    keyboard.add(exit)
    SetState('@'+message.from_user.username,6,cursor,db)
    bot.send_message(message.chat.id,"Статус изменен. Выберите дальнейшее действие",reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('delete'))
def editing11(call):
    if(call.data[-1]=='%'):
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if (GetRang('@' + call.from_user.username, cursor) in [9, 10] or GetSecondRang(
                '@' + call.from_user.username, cursor) in [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard,parse_mode='HTML')
    else:
        nick_and_id=call.data[7:]
        words=nick_and_id.split('*')
        nick=words[0]
        id=words[1]
        DeleteUserFromProject(nick,id,cursor,db)
        members = GetMembersOfProject(id, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for member in members:
            keyboard.add(telebot.types.InlineKeyboardButton(text=member[0], callback_data='delete_' + member[0] + '*' + str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='delete_%'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text='Выберите курсанта из списка участников', reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 22)
def editing2(message):
    nick = message.text
    if (nick[0] != '@'):
        nick = "@" + nick
    if(nick=='@Закончить'):
        SetState('@'+message.from_user.username, 6, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if (GetRang('@' + message.from_user.username, cursor) in [9, 10] or GetSecondRang(
                '@' + message.from_user.username, cursor) in [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id,'Изменения приняты. Выберите дальнейшее действие', reply_markup=keyboard)
    elif (IsUserInDB(nick, cursor, db)):
        if (GetRang(nick, cursor) in [2, 3, 4]):
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хипстер',callback_data='adding_2'+nick))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хастлер',callback_data='adding_3'+nick))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хакер',callback_data='adding_4'+nick))
            bot.send_message(message.chat.id, 'Какова его роль в проекте?',reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Это не курсант, попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('adding'))
def editing3(call):
    role=call.data[7]
    nick=call.data[8:]
    AddToProject(GetCurrProject('@'+call.from_user.username,cursor),nick,role,cursor,db)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text="Принято")

project_info={}
@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 21)
def new_project2(message):
    project_info['name']=message.text
    bot.send_message(message.chat.id, 'Выберите лидера команды из числа курсантов и введите его никнейм')
    SetState("@" + message.from_user.username, 210, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 210)
def new_project21(message):
    nick = message.text
    if (nick[0] != '@'):
        nick = "@" + nick
    if(IsUserInDB(nick,cursor,db)):
        if (GetRang(nick, cursor) in [2, 3, 4]):
            project_info['leader'] = nick
            keyboard=telebot.types.InlineKeyboardMarkup()
            first=telebot.types.InlineKeyboardButton(text='Учебный',callback_data='type_1')
            second = telebot.types.InlineKeyboardButton(text='Рабочий', callback_data='type_2')
            keyboard.add(first)
            keyboard.add(second)
            bot.send_message(message.chat.id, 'Выберите тип проекта:',reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Это не курсант, попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе')

experts=[]
@bot.callback_query_handler(func=lambda call: True and call.data.startswith('type'))
def new_project3(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Веберите тип проекта:")
    num=call.data[-1]
    project_info['type'] = num
    experts.append('@'+call.from_user.username)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('Закончить')
    bot.send_message(call.message.chat.id,
                     'Так как вы инициировали проект, вы являетесь его главным экспертом.Если вы хотите добавить еще экспертов, введите их никнеймы, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                     reply_markup=keyboard)
    SetState("@" + call.from_user.username, 212, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 212)
def new_project4(message):
    nick = message.text
    if (nick == 'Закончить'):
        project_info['experts']=experts
        SetState("@" + message.from_user.username, 6, cursor, db)
        CreateProject(project_info,cursor,db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if (GetRang('@' + message.from_user.username, cursor) in [9, 10] or GetSecondRang(
                '@' + message.from_user.username, cursor) in [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id,'Проект "'+project_info['name']+'" успешно создан. Выберите дальнейшее действие', reply_markup=keyboard)
    else:
        if (nick[0] != '@'):
            nick = "@" + nick
        if(IsUserInDB(nick,cursor,db)):
            if (GetRang(nick, cursor) in [6,10] or GetSecondRang(nick,cursor) in [6,10]):
                experts.append(nick)
                bot.send_message(message.chat.id, "Принято")
            else:
                bot.send_message(message.chat.id, "Этот пользователь не может быть экспертом")
        else:
            bot.send_message(message.chat.id, "Такого пользователя нет в базе")

@bot.message_handler(commands=["hi"])
def hi(message):
    bot.send_message(message.chat.id, message.chat.type,reply_markup=get_keyboard(GetRang('@'+message.from_user.username,cursor),GetSecondRang('@'+message.from_user.username,cursor)))

@bot.message_handler(commands=["vote"])
def start_voting(message):
    if(message.chat.type=='private'):
        rang=GetRang('@'+message.from_user.username,cursor)
        second_rang=GetSecondRang('@'+message.from_user.username,cursor)
        if(rang==2):
            SetCurrentFighterVoting('@'+message.from_user.username,0,cursor,db)
            config.fighters_list = GetListOfFirstFlow('@' + message.from_user.username, cursor)
            config.fighters_num=len(config.fighters_list)
            info=[]
            for i in range(0,6): info.append(0)
            config.fighters_marks['@'+message.from_user.username]=info
            bot.send_message(message.chat.id,'Оценка нематериального вклада.\nОсь отношений, первый курс \nКурсант: '+
                             config.fighters_list[GetCurrentFighterVoting('@'+message.from_user.username,cursor)][0]+
                             '\nЧестность: 0 \nЯсность позиции: 0 \nУровень энергии: 0 \nУстойчивость личностного роста: 0 \nИнтенсивность личностного роста: 0 \nЭффективность работы в команде: 0',
                             reply_markup=config.ChooseKeyboardForFirstFlowRelations('@'+message.from_user.username,cursor))
        elif rang==3 and IsInProject('@'+message.from_user.username,cursor):
            keyboard = telebot.types.InlineKeyboardMarkup()
            projects=GetProjects('@'+message.from_user.username,cursor)
            for project in projects:
                keyboard.add(telebot.types.InlineKeyboardButton(project[0], callback_data='project_decision_'+str(project[1])))
            bot.send_message(message.chat.id,'Выберите проект',reply_markup=keyboard)
        elif(rang==6 or second_rang==6):
            config.current_fighter_for_educator=0
            config.fighters_list = GetListOfFirstFlow('@'+message.from_user.username,cursor)
            config.fighters_num = len(config.fighters_list)
            config.educator_marks=[0,0,0,0]
            bot.send_message(message.chat.id, 'Оценка нематериального вклада.\nОсь дела, первый курс \nКурсант: ' +
                             config.fighters_list[0][0] +
                             '\nДвижение к цели: 0 \nРезультативность: 0 \nАдекватность картины мира: 0 \nВедение переговоров с внутренними и внешними референтными группами: 0',
                             reply_markup=config.ChooseKeyboardForFirstFlowBusiness())
        elif(rang==5 or second_rang==5 or second_rang==7):
            config.current_fighter_for_tutor=0
            config.tutor_marks=[0,0,0,0,0]
            config.second_flow_list=GetListOfSecondFlow('@'+message.from_user.username,cursor)
            config.second_flow_num=len(config.second_flow_list)
            bot.send_message(message.chat.id, 'Оценка нематериального вклада.\nОсь отношений, второй курс \nКурсант: ' +
                             config.second_flow_list[0][0] +
                             '\nЧестность: 0 \nЯсность позиции: 0 \nУровень энергии: 0 \nУстойчивость личностного роста: 0 \nИнтенсивность личностного роста: 0',
                             reply_markup=config.ChooseKeyboardForSecondFlowRelations())
        elif(rang==10 or second_rang==10):
            config.current_fighter_for_expert = 0
            config.second_flow_list = GetListOfSecondFlow('@' + message.from_user.username, cursor)
            config.second_flow_num = len(config.second_flow_list)
            config.expert_marks = [0, 0, 0, 0, 0]
            bot.send_message(message.chat.id, 'Оценка нематериального вклада.\nОсь дела, второй курс \nКурсант: ' +
                             config.second_flow_list[0][0] +
                             '\nДвижение к цели: 0 \nРезультативность: 0 \nАдекватность картины мира: 0 \nВедение переговоров с внутренними и внешними референтными группами: 0\n Эффективность работы в команде: 0',
                             reply_markup=config.ChooseKeyboardForSecondFlowBusiness())
        elif(GetAuthority('@'+message.from_user.username,cursor)>0):
            keyboard=telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton('Оценить курсантов 1 курса',callback_data='decision_1'))
            keyboard.add(telebot.types.InlineKeyboardButton('Оценить курсантов 2 курса', callback_data='decision_2'))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('project_decision'))
def choose_project_voting(call):
    project_id=call.data[17:]
    config.project_members=GetMembersOfProjectForVoting('@'+call.from_user.username,project_id,cursor)
    config.current_project_member=0
    config.project_marks=[0,0,0,0,0]
    config.current_project=GetProjectById(project_id,cursor)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                     text='Оценка нематериального вклада.\nОсь дела, второй курс.\n Проект: '+config.current_project+' \nКурсант: ' +config.project_members[0][0] +
                     '\nДвижение к цели: 0 \nРезультативность: 0 \nАдекватность картины мира: 0 \nВедение переговоров с внутренними и внешними референтными группами: 0\n Эффективность работы в команде: 0',
                     reply_markup=config.ChooseKeyboardForSecondFlowProjectBusiness())

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('decision'))
def choose_flow(call):
    decision=call.data[-1]
    if decision==1:
        config.current_fighter_for_authority = 0
        config.fighters_list = GetListOfFirstFlow('@' + call.from_user.username, cursor)
        config.fighters_num = len(config.fighters_list)
        config.authority_first_marks = [0, 0, 0, 0, 0]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь власти, первый курс \nКурсант: ' +config.fighters_list[0][0] +
                         '\nРазвитие парадигмы децентрализации:0 \nСтратегическое развитие сообщества:0 \nУправление ресурсами:0 \nУправляемость проектов:0\nПроф. доверие:0',
                         reply_markup=config.ChooseKeyboardForFirstFlowAuthority())
    elif decision==2:
        config.current_second_flow_for_authority = 0
        config.second_flow_list=GetListOfSecondFlow('@' + call.from_user.username, cursor)
        config.second_flow_num = len(config.second_flow_list)
        config.authority_second_marks = [0, 0, 0, 0, 0]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь власти, второй курс \nКурсант: ' + config.second_flow_list[0][
                                  0] +
                                   '\nРазвитие парадигмы децентрализации:0 \nСтратегическое развитие сообщества:0 \nУправление ресурсами:0 \nУправляемость проектов:0\nПроф. доверие:0',
                              reply_markup=config.ChooseKeyboardForSecondFlowAuthority())

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('first_flow_relations'))
def fighters_vote(call):
    if call.data[-1]!="8":
        if call.data[-1] == "1":
            config.fighters_marks['@' + call.from_user.username][0]= 1 if config.fighters_marks['@' + call.from_user.username][0]==0 else 0
        elif call.data[-1] == "2":
            config.fighters_marks['@' + call.from_user.username][1] = 1 if config.fighters_marks['@' + call.from_user.username][1] == 0 else 0
        elif call.data[-1] == "3":
            config.fighters_marks['@' + call.from_user.username][2] = 1 if config.fighters_marks['@' + call.from_user.username][2] == 0 else 0
        elif call.data[-1] == "4":
            config.fighters_marks['@' + call.from_user.username][3]= 1 if config.fighters_marks['@' + call.from_user.username][3]==0 else 0
        elif call.data[-1] == "5":
            config.fighters_marks['@' + call.from_user.username][4]= 1 if config.fighters_marks['@' + call.from_user.username][4]==0 else 0
        elif call.data[-1] == "6":
            config.fighters_marks['@' + call.from_user.username][5]= 1 if config.fighters_marks['@' + call.from_user.username][5]==0 else 0
        elif call.data[-1] == '7':
            AddMark(config.fighters_list[GetCurrentFighterVoting('@' + call.from_user.username, cursor)][0],config.fighters_marks['@'+call.from_user.username],1,1,cursor,db)
            SetCurrentFighterVoting('@'+call.from_user.username,str(GetCurrentFighterVoting('@'+call.from_user.username,cursor)+1),cursor,db)
            info=[]
            for i in range(0,6): info.append(0)
            config.fighters_marks['@'+call.from_user.username]=info

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь отношений, первый курс \nКурсант: ' +
                                   config.fighters_list[GetCurrentFighterVoting('@' + call.from_user.username, cursor)][0] +
                                   '\nЧестность:' + str(config.fighters_marks['@' + call.from_user.username][0]) +
                                   '\nЯсность позиции:' + str(config.fighters_marks['@' + call.from_user.username][1]) +
                                   '\nУровень энергии:' + str(config.fighters_marks['@' + call.from_user.username][2]) +
                                   '\nУстойчивость личностного роста:' + str(config.fighters_marks['@' + call.from_user.username][3]) +
                                   '\nИнтенсивность личностного роста:' + str(config.fighters_marks['@' + call.from_user.username][4]) +
                                   '\nЭффективность работы в команде:' + str(config.fighters_marks['@' + call.from_user.username][5]),
                              reply_markup=config.ChooseKeyboardForFirstFlowRelations('@' + call.from_user.username,cursor))
    else:
        AddMark(config.fighters_list[GetCurrentFighterVoting('@' + call.from_user.username, cursor)][0],config.fighters_marks['@' + call.from_user.username], 1, 1, cursor, db)
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('first_flow_business'))
def educator_votes(call):
    if call.data[-1]!='6':
        if call.data[-1]=='1':
            config.educator_marks[0]=1 if config.educator_marks[0]==0 else 0
        if call.data[-1]=='2':
            config.educator_marks[1]=1 if config.educator_marks[1]==0 else 0
        if call.data[-1]=='3':
            config.educator_marks[2]=1 if config.educator_marks[2]==0 else 0
        if call.data[-1]=='4':
            config.educator_marks[3]=1 if config.educator_marks[3]==0 else 0
        if call.data[-1]=='5':
            AddMark(config.fighters_list[config.current_fighter_for_educator][0],config.educator_marks,2,1,cursor,db)
            config.current_fighter_for_educator+=1
            config.educator_marks=[0,0,0,0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь дела, первый курс \nКурсант: ' +
                                   config.fighters_list[config.current_fighter_for_educator][0] +
                                   '\nДвижение к цели:' + str(config.educator_marks[0]) + '\nРезультативность:' + str(
                                  config.educator_marks[1]) +
                                   '\nАдекватность картины мира:' + str(config.educator_marks[2]) +
                                   '\nВедение переговоров с внутренними и внешними референтными группами:' + str(
                                  config.educator_marks[3]),
                              reply_markup=config.ChooseKeyboardForFirstFlowBusiness())
    else:
        AddMark(config.fighters_list[config.current_fighter_for_educator][0], config.educator_marks, 2, 1, cursor, db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id,'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('first_flow_authority'))
def authority_votes1(call):
    if call.data[-1]!='7':
        if call.data[-1]=='1':
            config.authority_first_marks[0]=1 if config.authority_first_marks[0]==0 else 0
        if call.data[-1]=='2':
            config.authority_first_marks[1] = 1 if config.authority_first_marks[1] == 0 else 0
        if call.data[-1]=='3':
            config.authority_first_marks[2] = 1 if config.authority_first_marks[2] == 0 else 0
        if call.data[-1]=='4':
            config.authority_first_marks[3] = 1 if config.authority_first_marks[3] == 0 else 0
        if call.data[-1]=='5':
            config.authority_first_marks[4] = 1 if config.authority_first_marks[4] == 0 else 0
        if call.data[-1]=='6':
            AddMark(config.fighters_list[config.current_fighter_for_authority][0],config.authority_first_marks,3,1,cursor,db)
            config.current_fighter_for_authority+=1
            config.authority_first_marks=[0,0,0,0,0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь власти, первый курс \nКурсант: ' +
                                   config.fighters_list[config.current_fighter_for_authority][0] +
                                   '\nРазвитие парадигмы децентрализации:' + str(config.authority_first_marks[0]) +
                                   '\nСтратегическое развитие сообщества:' + str(config.authority_first_marks[1]) +
                                   '\nУправление ресурсами:' + str(config.authority_first_marks[2]) +
                                   '\nУправляемость проектов:' + str(config.authority_first_marks[3])+
                                   '\nПроф. доверие:' + str(config.authority_first_marks[4]),
                              reply_markup=config.ChooseKeyboardForFirstFlowAuthority())
    else:
        AddMark(config.fighters_list[config.current_fighter_for_authority][0], config.authority_first_marks, 3, 1, cursor,db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_relations'))
def tutor_votes(call):
    if call.data[-1]!="7":
        if call.data[-1] == "1":
            config.tutor_marks[0]= 1 if config.tutor_marks[0]==0 else 0
        elif call.data[-1] == "2":
            config.tutor_marks[1]= 1 if config.tutor_marks[1]==0 else 0
        elif call.data[-1] == "3":
            config.tutor_marks[2]= 1 if config.tutor_marks[2]==0 else 0
        elif call.data[-1] == "4":
            config.tutor_marks[3]= 1 if config.tutor_marks[3]==0 else 0
        elif call.data[-1] == "5":
            config.tutor_marks[4]= 1 if config.tutor_marks[4]==0 else 0
        elif call.data[-1] == '6':
            AddMark(config.second_flow_list[config.current_fighter_for_tutor][0],config.tutor_marks,1,2,cursor,db)
            config.current_fighter_for_tutor+=1
            config.tutor_marks=[0,0,0,0,0]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь отношений, второй курс \nКурсант: ' +
                                   config.second_flow_list[config.current_fighter_for_tutor][0] +
                                   '\nЧестность: '+str(config.tutor_marks[0])+'\nЯсность позиции: '+str(config.tutor_marks[1])+
                                   '\nУровень энергии: '+str(config.tutor_marks[2])+'\nУстойчивость личностного роста: '+str(config.tutor_marks[3])+
                                   '\nИнтенсивность личностного роста: '+str(config.tutor_marks[4]),
                              reply_markup=config.ChooseKeyboardForSecondFlowRelations())
    else:
        AddMark(config.second_flow_list[config.current_fighter_for_tutor][0],config.tutor_marks,1,2,cursor,db)
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_business'))
def expert_votes(call):
    if call.data[-1]!='7':
        if call.data[-1]=='1':
            config.expert_marks[0]=1 if config.expert_marks[0]==0 else 0
        elif call.data[-1]=='2':
            config.expert_marks[1]=1 if config.expert_marks[1]==0 else 0
        elif call.data[-1]=='3':
            config.expert_marks[2]=1 if config.expert_marks[2]==0 else 0
        elif call.data[-1]=='4':
            config.expert_marks[3]=1 if config.expert_marks[3]==0 else 0
        elif call.data[-1]=='5':
            config.expert_marks[4]=1 if config.expert_marks[4]==0 else 0
        elif call.data[-1]=='6':
            AddMark(config.second_flow_list[config.current_fighter_for_expert][0],config.expert_marks,2,2,cursor,db)
            config.current_fighter_for_expert+=1
            config.expert_marks=[0,0,0,0,0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь дела, второй курс \nКурсант: ' +
                                   config.second_flow_list[config.current_fighter_for_expert][0] +
                                   '\nДвижение к цели: '+str(config.expert_marks[0])+' \nРезультативность: '+str(config.expert_marks[1])+
                                   '\nАдекватность картины мира: '+str(config.expert_marks[2])+
                                   '\nВедение переговоров с внутренними и внешними референтными группами: '+str(config.expert_marks[3])+
                                   '\n Эффективность работы в команде: '+str(config.expert_marks[4]),
                              reply_markup=config.ChooseKeyboardForSecondFlowBusiness())
    else:
        AddMark(config.second_flow_list[config.current_fighter_for_expert][0], config.expert_marks, 2, 2, cursor, db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_projects'))
def voting_in_project(call):
    if call.data[-1]!='7':
        if call.data[-1]=='1':
            config.project_marks[0]=1 if config.project_marks[0]==0 else 0
        elif call.data[-1]=='2':
            config.project_marks[1]=1 if config.project_marks[1]==0 else 0
        elif call.data[-1]=='3':
            config.project_marks[2]=1 if config.project_marks[2]==0 else 0
        elif call.data[-1]=='4':
            config.project_marks[3]=1 if config.project_marks[3]==0 else 0
        elif call.data[-1]=='5':
            config.project_marks[4]=1 if config.project_marks[4]==0 else 0
        elif call.data[-1]=='6':
            AddMarkFromProject(config.project_members[config.current_project_member][0],config.project_marks,2,2,cursor,db)
            config.current_project_member+=1
            config.project_marks=[0,0,0,0,0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь дела, второй курс.\nПроект: '+config.current_project+' \nКурсант: ' +
                                   config.project_members[config.current_project_member][0] +
                                   '\nДвижение к цели: '+str(config.project_marks[0])+' \nРезультативность: '+str(config.project_marks[1])+
                                   '\nАдекватность картины мира: '+str(config.project_marks[2])+
                                   '\nВедение переговоров с внутренними и внешними референтными группами: '+str(config.project_marks[3])+
                                   '\n Эффективность работы в команде: '+str(config.project_marks[4]),
                              reply_markup=config.ChooseKeyboardForSecondFlowProjectBusiness())
    else:
        AddMarkFromProject(config.project_members[config.current_project_member][0], config.project_marks, 2, 2, cursor,db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_authority'))
def authority_votes2(call):
    if call.data[-1]!='7':
        if call.data[-1]=='1':
            config.authority_second_marks[0]=1 if config.authority_second_marks[0]==0 else 0
        if call.data[-1]=='2':
            config.authority_second_marks[1] = 1 if config.authority_second_marks[1] == 0 else 0
        if call.data[-1]=='3':
            config.authority_second_marks[2] = 1 if config.authority_second_marks[2] == 0 else 0
        if call.data[-1]=='4':
            config.authority_second_marks[3] = 1 if config.authority_second_marks[3] == 0 else 0
        if call.data[-1]=='5':
            config.authority_second_marks[4] = 1 if config.authority_second_marks[4] == 0 else 0
        if call.data[-1]=='6':
            AddMark(config.second_flow_list[config.current_second_flow_for_authority][0],config.authority_second_marks,3,2,cursor,db)
            config.current_second_flow_for_authority+=1
            config.authority_second_marks=[0,0,0,0,0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
                                   config.second_flow_list[config.current_second_flow_for_authority][0] +
                                   '\nРазвитие парадигмы децентрализации:' + str(config.authority_second_marks[0]) +
                                   '\nСтратегическое развитие сообщества:' + str(config.authority_second_marks[1]) +
                                   '\nУправление ресурсами:' + str(config.authority_second_marks[2]) +
                                   '\nУправляемость проектов:' + str(config.authority_second_marks[3])+
                                   '\nПроф. доверие:' + str(config.authority_second_marks[4]),
                              reply_markup=config.ChooseKeyboardForSecondFlowAuthority())
    else:
        AddMark(config.second_flow_list[config.current_second_flow_for_authority][0], config.authority_second_marks, 3, 2, cursor, db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))

@bot.message_handler(commands=["id"])
def get_id(message):
    if(message.chat.type=='private'):
        SetChatId('@'+message.from_user.username,message.chat.id,cursor,db)
        bot.send_message(message.chat.id,'Ok',
                         reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                   GetSecondRang('@' + message.from_user.username, cursor)))


budget_info=[]
@bot.message_handler(commands=["budget"])
def send_budget_offer(message):
    if(GetRang('@'+message.from_user.username,cursor)==9 or GetSecondRang('@'+message.from_user.username,cursor)==9):
        if(IsThereActiveVoting(cursor)):
            bot.send_message(message.chat.id,'В данный момент уже проходит голосование за утверждение бюджета',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))
        else:
            bot.send_message(message.chat.id,'Введите предполагаемую сумму бюджета')
            SetState('@'+message.from_user.username,51,cursor,db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 51)
def enter_budget_money(message):
    summa = message.text
    config.budget=summa
    budget_info.append(summa)
    bot.send_message(message.chat.id, 'Вставьте ссылку на документ со сметой')
    SetState('@' + message.from_user.username, 52, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 52)
def enter_budget_money(message):
    url = message.text
    budget_info.append(url)
    count = bot.get_chat_members_count(message.chat.id) - 1
    StartVoting(message.chat.id, '@' + message.from_user.username, count, cursor, db)
    bot.send_message(message.chat.id,
                     'Утверждается бюджет на следующий месяц\nПодробности по ссылке: ' + url + '\nИтоговая сумма: ' + budget_info[0])
    members = GetListOfUsers(cursor)
    SetState('@' + message.from_user.username, 6, cursor, db)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="За", callback_data="voting_1"),telebot.types.InlineKeyboardButton(text="Против", callback_data="voting_2"))
    for i in range(0, len(members)):
        if (members[i][3] != None and members[i][0]!='@'+message.from_user.username):
            bot.send_message(members[i][3],
                             'Началось голосование за утверждение бюджета. Подробности по ссылке: ' + url + '\nИтоговая сумма: ' + budget_info[0] +
                             '\nВыразите ваше мнение', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('voting'))
def voting(call):
    BudgetVote(call.data[-1], cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,'Спасибо за ваш голос! Текущий прогресс голосования:\n'+BudgetInfo(cursor),
                          reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                    GetSecondRang('@' + call.from_user.username, cursor)))

@bot.message_handler(commands=["finish_budget"])
def finish_budget(message):
    if(GetRang('@'+message.from_user.username,cursor)==9 or GetSecondRang('@'+message.from_user.username,cursor)==9):
        if not(IsThereActiveVoting(cursor)):
            bot.send_message(message.chat.id,'На данный момент активных голосований нет',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))
        else:
            if(GetUserWhoStartedVoting(cursor)=='@'+message.from_user.username):
                bot.send_message(message.chat.id, 'Утверждение бюджета завершено. Результат:\n' + BudgetInfo(cursor),
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
                FinishVoting(cursor,db)
            else:
                bot.send_message(message.chat.id,'Голосование может завершить только тот, кто его начал',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))

@bot.message_handler(commands=["marks"])
def marks(message):
    if (message.chat.type == 'private'):
        if (GetRang(message.from_user.username, cursor) in range(2, 10)):
            words = message.text.split(' ')
            marks = []
            user=''
            if (len(words) > 1 and (
                    GetRang(message.from_user.username, cursor) not in [5, 6, 7, 9, 11] and GetSecondRang(
                    message.from_user.username, cursor) not in [5, 6, 7, 9, 11]) and words[0]!='Посмотреть'):
                return
            if (len(words) > 1 and words[0]!='Посмотреть'):
                user = words[1]
                if (user[0] != '@'):
                    user = "@" + user
                if not(IsUserInDB(user, cursor, db)):
                    bot.send_message(message.chat.id, "Такого польователя нет в базе",
                                     reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                               GetSecondRang('@' + message.from_user.username, cursor)))
                    return
            else:
                user='@' + message.from_user.username
            if GetRang(user, cursor) not in [2, 3]:
                bot.send_message(message.chat.id, 'Оценки можно просмотреть только у курсантов',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
                return
            if GetRang(user,cursor)==2:
                marks = MarksOfFirstFlow(user, cursor)
            else:
                marks=MarksOfSecondFlow(user,cursor)
            if(len(marks)>0):
                for i in range(0,len(marks)):
                    if marks[i]==2:
                        marks[i]=0.5
                for mark in marks:
                    axis=int(mark[1])
                    if axis==1:
                        if GetRang(user, cursor) == 2:
                            bot.send_message(message.chat.id,'Оценки по оси отношений от '+mark[2][1:]+':\nЧестность: '+mark[0][1]+
                                             '\nЯсность позиции: '+mark[0][2]+'\nУровень энергии: '+mark[0][3]+'\nУстойчивость личностного роста: '+mark[0][4]+
                                             '\nИнтенсивность личностного роста: '+mark[0][5]+'\nЭффективность работы в команде: '+mark[0][6])
                        else:
                            bot.send_message(message.chat.id,
                                             'Оценки по оси отношений от ' + mark[2][1:] + ':\nЧестность: ' + mark[0][1] +
                                             '\nЯсность позиции: ' + mark[0][2] + '\nУровень энергии: ' + mark[0][3] + '\nУстойчивость личностного роста: ' + mark[0][4] +
                                             '\nИнтенсивность личностного роста: ' + mark[0][5])
                    elif axis==2:
                        if GetRang(user, cursor) == 2:
                            bot.send_message(message.chat.id,
                                             'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение к цели: ' + mark[0][1] +
                                             '\nРезультативность: ' + mark[0][2] + '\nАдекватность картины мира: ' + mark[0][3] +
                                             '\nВедение переговоров с внутренними и внешними референтными группами: ' + mark[0][4])
                        else:
                            bot.send_message(message.chat.id,
                                             'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение к цели: ' + mark[0][1] +
                                             '\nРезультативность: ' + mark[0][2] + '\nАдекватность картины мира: ' +mark[0][3] +
                                             '\nВедение переговоров с внутренними и внешними референтными группами: ' +mark[0][4]+
                                             '\nЭффективность работы в команде: '+mark[0][5])
                    elif axis==3:
                        bot.send_message(message.chat.id,
                                             'Оценки по оси власти от ' + mark[2][1:] + ':\nРазвитие парадигмы децентрализации: ' + mark[0][1] +
                                             '\nСтратегическое развитие сообщества: ' + mark[0][2] + '\nУправление ресурсами: ' + mark[0][3] +
                                             '\nУправляемость проектов: ' + mark[0][4]+'\nПроф. доверие: ' + mark[0][5])
            else:
                bot.send_message(message.chat.id,'Для данного польователя пока нет оценок',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
            bot.send_message(message.chat.id,'',reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                   GetSecondRang('@' + message.from_user.username, cursor)))

@bot.message_handler(commands=["order_buy"])
def buy_token(message):
    if(message.chat.type=='private'):
        if(GetRang('@'+message.from_user.username,cursor)==8 or GetSecondRang('@'+message.from_user.username,cursor)==8):
            bot.send_message(message.chat.id,'Сколько токенов вы хотите купить?')
            SetState('@'+message.from_user.username,30,cursor,db)

buy_info=[]
@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 30)
def enter_tokens(message):
    tokens=message.text
    buy_info.append(tokens)
    bot.send_message(message.chat.id,'За сколько вы хотите их купить?')
    SetState('@' + message.from_user.username, 31, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 31)
def enter_money(message):
    money=message.text
    buy_info.append(money)
    investors = GetInvestors('@' + message.from_user.username, cursor)
    id = CreateOrder('@' + message.from_user.username, 1, cursor, db)
    for investor in investors:
        bot.send_message(investor[0], '<b>Предложение №' + str(
            id) + '</b>\nПользователь @' + message.from_user.username + ' хочет продать ' + str(sell_info[0]) + ' токенов за '
                         + str(sell_info[1]) + ' эфиров.', parse_mode='HTML')
    bot.send_message(message.chat.id, 'Ваш запрос разослан остальным инвесторам. Номер вашего запроса - ' + str(id) +
                     '. Для закрытия предложения в любой момент введите /order_close ' + str(id),
                     reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                               GetSecondRang('@' + message.from_user.username, cursor)))
    SetState('@' + message.from_user.username, 6, cursor, db)

@bot.message_handler(commands=["order_sell"])
def sell_token(message):
    if (message.chat.type == 'private'):
        if (GetRang('@' + message.from_user.username, cursor) == 8 or GetSecondRang('@' + message.from_user.username,cursor) == 8):
            bot.send_message(message.chat.id, 'Сколько токенов вы хотите продать?')
            SetState('@' + message.from_user.username, 32, cursor, db)

sell_info = []
@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 32)
def enter_tokens2(message):
    tokens = message.text
    sell_info.append(tokens)
    bot.send_message(message.chat.id, 'За сколько вы хотите их продать?')
    SetState('@' + message.from_user.username, 33, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 33)
def enter_money2(message):
    money = message.text
    sell_info.append(money)
    investors = GetInvestors('@'+message.from_user.username,cursor)
    id = CreateOrder('@' + message.from_user.username, 2, cursor, db)
    for investor in investors:
        bot.send_message(investor[0], '<b>Предложение №'+str(id)+'</b>\nПользователь @' + message.from_user.username + ' хочет продать ' + str(
            sell_info[0]) + ' токенов за ' + str(sell_info[1]) + ' эфиров.',parse_mode='HTML')
    bot.send_message(message.chat.id, 'Ваш запрос разослан остальным инвесторам. Номер вашего запроса - '+str(id)+
                     '. Для закрытия предложения в любой момент введите /order_close '+str(id),
                     reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                               GetSecondRang('@' + message.from_user.username, cursor)))
    SetState('@' + message.from_user.username, 6, cursor, db)

@bot.message_handler(commands=["order_close"])
def close_offer(message):
    if(message.chat.type=='private' and (GetRang('@' + message.from_user.username, cursor) == 8 or GetSecondRang('@' + message.from_user.username,cursor) == 8)):
        words=message.text.split(' ')
        if len(words)>1:
            id=words[1]
            order_creator=CreatorOfOrder(id,cursor)
            user='@' + message.from_user.username
            if(user==order_creator):
                CloseOrder(id,cursor,db)
                investors = GetInvestors('@' + message.from_user.username, cursor)
                for investor in investors:
                    bot.send_message(investor[0], 'Предложение №' + str(id) + 'от пользователя @' + message.from_user.username + ' закрыто.')
                bot.send_message(message.chat.id, 'Предложение №' + str(id) + ' закрыто.',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
            else:
                bot.send_message(message.chat.id, 'Вы не можете закрыть это предложение',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
        else:
            bot.send_message(message.chat.id,'Ошибка в написании команды. Правильный формат: /order_close <order_id>',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))


@bot.message_handler(commands=["look_marks"])
def look_marks(message):
    if message.chat.type=='private' and (GetRang('@'+message.from_user.username,cursor) in [9,10,5] or GetSecondRang('@'+message.from_user.username,cursor) in [9,10,5]):
        students = GetListOfStudents(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for student in students:
            keyboard.add(telebot.types.InlineKeyboardButton(text=student[0], callback_data='look_marks_of_'+student[1]))
        keyboard.add(telebot.types.InlineKeyboardButton(text='<Вернуться в главное меню>', callback_data='look_marks_of_*'))
        bot.send_message(message.chat.id, 'Выберите курсанта', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_marks_of'))
def looking_marks(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data[-1] == '*':
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))
    else:
        user = call.data[14:]
        if GetRang(user, cursor) == 2:
            marks = MarksOfFirstFlow(user, cursor)
        else:
            marks = MarksOfSecondFlow(user, cursor)
        if (len(marks) > 0):
            for i in range(0, len(marks)):
                if marks[i] == 2:
                    marks[i] = 0.5
            for mark in marks:
                axis = int(mark[1])
                if axis == 1:
                    if GetRang(user, cursor) == 2:
                        bot.send_message(call.message.chat.id,
                                         'Оценки по оси отношений от ' + mark[2][1:] + ':\nЧестность: ' + mark[0][1] +
                                         '\nЯсность позиции: ' + mark[0][2] + '\nУровень энергии: ' + mark[0][
                                             3] + '\nУстойчивость личностного роста: ' + mark[0][4] +
                                         '\nИнтенсивность личностного роста: ' + mark[0][
                                             5] + '\nЭффективность работы в команде: ' + mark[0][6])
                    else:
                        bot.send_message(call.message.chat.id,
                                         'Оценки по оси отношений от ' + mark[2][1:] + ':\nЧестность: ' + mark[0][1] +
                                         '\nЯсность позиции: ' + mark[0][2] + '\nУровень энергии: ' + mark[0][
                                             3] + '\nУстойчивость личностного роста: ' + mark[0][4] +
                                         '\nИнтенсивность личностного роста: ' + mark[0][5])
                elif axis == 2:
                    if GetRang(user, cursor) == 2:
                        bot.send_message(call.message.chat.id,
                                         'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение к цели: ' + mark[0][1] +
                                         '\nРезультативность: ' + mark[0][2] + '\nАдекватность картины мира: ' + mark[0][
                                             3] +
                                         '\nВедение переговоров с внутренними и внешними референтными группами: ' + mark[0][
                                             4])
                    else:
                        bot.send_message(call.message.chat.id,
                                         'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение к цели: ' + mark[0][1] +
                                         '\nРезультативность: ' + mark[0][2] + '\nАдекватность картины мира: ' + mark[0][
                                             3] +
                                         '\nВедение переговоров с внутренними и внешними референтными группами: ' + mark[0][
                                             4] +
                                         '\nЭффективность работы в команде: ' + mark[0][5])
                elif axis == 3:
                    bot.send_message(call.message.chat.id,
                                     'Оценки по оси власти от ' + mark[2][1:] + ':\nРазвитие парадигмы децентрализации: ' +
                                     mark[0][1] +
                                     '\nСтратегическое развитие сообщества: ' + mark[0][2] + '\nУправление ресурсами: ' +
                                     mark[0][3] +
                                     '\nУправляемость проектов: ' + mark[0][4] + '\nПроф. доверие: ' + mark[0][5])
        else:
            bot.send_message(call.message.chat.id, 'Для данного польователя пока нет оценок',
                             reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                       GetSecondRang('@' + call.from_user.username, cursor)))
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))


@bot.message_handler(commands=["look_profiles"])
def look_profiles(message):
    if message.chat.type=='private' and (GetRang('@'+message.from_user.username,cursor) in [9,10,8,5] or GetSecondRang('@'+message.from_user.username,cursor) in [9,10,8,5]):
        students = GetListOfStudents(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for student in students:
            keyboard.add(telebot.types.InlineKeyboardButton(text=student[0], callback_data='look_profile_of_'+student[1]))
        keyboard.add(telebot.types.InlineKeyboardButton(text='<Вернуться в главное меню>', callback_data='look_profile_of_*'))
        bot.send_message(message.chat.id, 'Выберите курсанта', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_profile_of'))
def looking_profile(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data[-1] == '*':
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                   GetSecondRang('@' + call.from_user.username, cursor)))
    else:
        profile=GetProfile(call.data[16:], cursor)
        if profile[0] != None:
            string = 'Курсант: ' + profile[0]
            string += "\nФото: "
            bot.send_message(call.message.chat.id, string)
            bot.send_photo(call.message.chat.id, profile[3])
            string = "Телефон: " + str(profile[1])
            string = string + "\nЭлектронная почта: " + profile[2]
            string = string + "\nДата регистрации: " + profile[6]
            string = string + '\nАвторитет: ' + str(profile[4])
            if profile[7] == None:
                profile[7] = 0
            string = string + '\nСумма оценок в текущем месяце: ' + str(profile[7])
            if profile[8] != None:
                string = string + '\nДосье: ' + profile[8]
            bot.send_message(call.message.chat.id, string,
                             reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                       GetSecondRang('@' + call.from_user.username, cursor)))
        else:
            bot.send_message(call.message.chat.id, "Ой, анкета еще не заполнена",
                             reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                       GetSecondRang('@' + call.from_user.username, cursor)))


@bot.message_handler(commands=["set_rang"])
def set_rang(message):
    if(message.chat.type=='private' and (GetRang('@'+message.from_user.username,cursor)==9 or GetSecondRang('@'+message.from_user.username,cursor)==9)):
        words=message.text.split(' ')
        if(len(words)>1):
            nick=words[1]
            if(nick[0]!='@'): nick='@'+nick
            if(IsUserInDB(nick,cursor,db)):
                keyboard=telebot.types.InlineKeyboardMarkup()
                keyboard.row(telebot.types.InlineKeyboardButton(text='Первый курс',callback_data='set_rang_2#'+nick),
                             telebot.types.InlineKeyboardButton(text='Второй курс', callback_data='set_rang_3#' + nick),
                             telebot.types.InlineKeyboardButton(text='Третий курс', callback_data='set_rang_4#' + nick))
                keyboard.row(telebot.types.InlineKeyboardButton(text='Тьютор', callback_data='set_rang_5#' + nick),
                             telebot.types.InlineKeyboardButton(text='Преподаватель',callback_data='set_rang_6#' + nick),
                             telebot.types.InlineKeyboardButton(text='Завуч', callback_data='set_rang_11#' + nick))
                keyboard.row(telebot.types.InlineKeyboardButton(text='Сталкер', callback_data='set_rang_7#' + nick),
                             telebot.types.InlineKeyboardButton(text='Эксперт', callback_data='set_rang_10#' + nick))
                keyboard.row(telebot.types.InlineKeyboardButton(text='Инвестор', callback_data='set_rang_8#' + nick),
                             telebot.types.InlineKeyboardButton(text='Администратор',callback_data='set_rang_9#' + nick))
                bot.send_message(message.chat.id,'Выберите роль для пользователя '+nick,reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id,'Такого пользователя нет в базе',
                                 reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                           GetSecondRang('@' + message.from_user.username, cursor)))
        else:
            bot.send_message(message.chat.id, 'Ошибка в написании команды. Правильный формат: /set_rang <nickname>',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('set_rang'))
def set_rang(call):
    text=call.data[9:]
    words=text.split('#')
    rang=int(words[0])
    nick=words[1]
    if rang in [2,3,4,5,6]:
        SetRang(nick,rang,cursor,db)
    else:
        SetSecondRang(nick,rang,cursor,db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,"Успешно",
                     reply_markup=get_keyboard(GetRang('@' + call.from_user.username, cursor),
                                                    GetSecondRang('@' + call.from_user.username, cursor)))


@bot.message_handler(content_types=["text"])
def text(message):
    if message.chat.type == 'private':
        if message.from_user.username=='robertlengdon':
            bot.send_message(message.chat.id,'Вадим, ты шо, ебнутый?')
        mess = message.text
        print(message.text)
        if mess == '📂 Проекты':
            projectsMenu(message)
        elif mess == '📊 Оценки':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.add('Оценить нематериальный вклад участников')
            if(GetRang('@'+message.from_user.username,cursor) in [2,3,4]):
                keyboard.add('Посмотреть свои оценки')
            if GetRang('@'+message.from_user.username,cursor) in [9,10,8,5] or GetSecondRang('@'+message.from_user.username,cursor) in [9,10,8,5]:
                keyboard.add('Оценки пользователей')
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Оценки"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == 'Оценить нематериальный вклад участников':
            start_voting(message)
        elif mess == 'Посмотреть свои оценки':
            marks(message)
        elif mess == '📋 Профиль':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row('Посмотреть профиль','Редактировать профиль','Сбросить профиль')
            if GetRang('@'+message.from_user.username,cursor) in [9,10,8,5] or GetSecondRang('@'+message.from_user.username,cursor) in [9,10,8,5]:
                keyboard.add('Профили пользователей')
            keyboard.add(emojize('Назад'))
            bot.send_message(message.chat.id, 'Вкладка <b>"Профиль"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '➕📓 Добавить абитуриентов':
            add_abit(message)
        elif mess == '👔 Функции администратора':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row(emojize(':heavy_plus_sign::notebook: Добавить абитуриентов'),
                        emojize(':heavy_plus_sign::money_with_wings: Добавить инвесторов'))
            if IsThereActiveVoting(cursor):
                 keyboard.add('Закончить утверждение бюджета')
            else:
                 keyboard.add(emojize(':loudspeaker: Начать голосование за утверждение бюджета'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Администратор"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '💳 Функции инвестора':
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row('Купить токены у пользователей', 'Продать токены пользователям')
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Инвестор"</b>', reply_markup=keyboard,parse_mode='HTML')
        elif mess == 'Посмотреть профиль':
            get_profile(message)
        elif mess == 'Редактировать профиль':
            red_profile(message)
        elif mess == 'Сбросить профиль':
            reset(message)
        elif mess == '➕💸 Добавить инвесторов':
            add_investor(message)
        elif mess == 'Профили пользователей':
            look_profiles(message)
        elif mess == 'Оценки пользователей':
            look_marks(message)
        elif mess == "Создать новый проект":
            project_switch(message,1)
        elif mess == "Редактировать проект":
            project_switch(message, 2)
        elif mess == "Список проектов":
            project_switch(message, 3)
        elif mess == 'Назад':
            bot.send_message(message.chat.id, 'Главное меню',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))
        elif mess == '📢 Начать голосование за утверждение бюджета':
            send_budget_offer(message)
        elif mess == 'Закончить утверждение бюджета':
            finish_budget(message)
        elif mess in ['hi','Hi','Привет','привет','hello','Hello']:
            bot.send_message(message.chat.id, 'Привет, ' + '@' + message.from_user.username,
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))
        else:
            bot.send_message(message.chat.id,'Неизвестная команда',
                             reply_markup=get_keyboard(GetRang('@' + message.from_user.username, cursor),
                                                       GetSecondRang('@' + message.from_user.username, cursor)))


#cursor.execute('ALTER TABLE marks ADD flow INTEGER')
#cursor.execute('ALTER TABLE users ADD sum_of_marks REAL')
#cursor.execute('INSERT INTO rangs (title) VALUES("Head teacher")')
#cursor.execute('INSERT INTO rangs (title) VALUES("Invited investor")')
#db.commit()
#cursor.execute('UPDATE users SET rang=9 WHERE nickname="@m_wizmo"')
#cursor.execute('UPDATE users SET second_rang=9 WHERE nickname="@m_wizmo"')
#cursor.execute('DELETE FROM users WHERE nickname="@абитуриентов"')
#cursor.execute('INSERT INTO users (nickname,rang) VALUES ("@robertlengdon",8)')
#cursor.execute('INSERT INTO users (nickname,rang) VALUES ("@Ed_corp",8)')
#cursor.execute('INSERT INTO users (nickname,rang) VALUES ("@DphoneK",8)')
#SetState('@m_wizmo',6,cursor,db)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,certificate=open(WEBHOOK_SSL_CERT, 'r'))
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
#bot.polling(none_stop=True)
