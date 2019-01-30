# -*- coding: utf-8 -*-
from db_commands.db_projects import *
from db_commands.db_users import *
from db_commands.db_profile import *
import telebot
from config import bot, db, cursor, get_keyboard, isRang

def projectsMenu(message):
    if (message.chat.type == 'private'):
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')


def project_switch(message, flag):
    if flag == 1:
        bot.send_message(message.chat.id, 'Введите название проекта')
        SetState("@" + message.from_user.username, 21, cursor, db)
    elif flag == 2:
        projects = GetProjects("@" + message.from_user.username, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        if len(projects) != 0:
            for i in range(0, len(projects)):
                keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],
                                                                callback_data='edit_project_' + str(projects[i][1])))
            bot.send_message(message.chat.id, 'Доступные для редактирования проекты', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Активных проектов нет',
                             reply_markup=get_keyboard('@' + message.from_user.username))
    elif flag == 3:
        projects = GetAllProjects(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        if len(projects) != 0:
            for i in range(0, len(projects)):
                keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],
                                                                callback_data='look_project_' + str(projects[i][1])))
            bot.send_message(message.chat.id, 'Все проекты "Корпуса"', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Активных проектов нет',
                             reply_markup=get_keyboard('@' + message.from_user.username))
    elif flag == 4:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, 'Работа с проектами завершена',
                         reply_markup=get_keyboard('@' + message.from_user.username))


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_project'))
def look_project(call):
    id = call.data[13:]
    info = GetProjectInfo(id, cursor)
    bot.send_message(call.message.chat.id, info, parse_mode='HTML')
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    new_project = "Создать новый проект"
    edit_project = "Редактировать проект"
    list_project = "Список проектов"
    exit = "Назад"
    flag = True
    if isRang(GetRangs('@' + call.from_user.username, cursor), [9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
        keyboard.add(edit_project)
    keyboard.add(list_project)
    keyboard.add(exit)
    bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('edit_project'))
def edit_project(call):
    id = call.data[13:]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Доступные для редактирования проекты")
    info = GetProjectInfo(id, cursor)
    bot.send_message(call.message.chat.id, info, parse_mode='HTML')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Добавить участника', callback_data='editing_project_1' + str(id)))
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Удалить участника', callback_data='editing_project_2' + str(id)))
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Изменить статус проекта', callback_data='editing_project_3' + str(id)))
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Пригласить экспертов', callback_data='editing_project_5' + str(id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Выход', callback_data='editing_project_4' + str(id)))
    bot.send_message(call.message.chat.id, 'Что вы хотите сделать?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('editing_project'))
def editing(call):
    id = call.data[17:]
    SetCurrProject(id, '@' + call.from_user.username, cursor, db)
    num = call.data[16]
    if num == '1':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('Закончить')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Введите никнеймы курсантов, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                         reply_markup=keyboard)
        username = "@" + call.from_user.username
        SetState(username, 22, cursor, db)
    elif num == '2':
        members = GetMembersOfProject(id, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for member in members:
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=member[0], callback_data='delete_' + member[0] + '*' + str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='delete_%'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите курсанта из списка участников', reply_markup=keyboard)
    elif num == '3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый статус проекта')
        SetCurrProject(id, '@' + call.from_user.username, cursor, db)
        SetState('@' + call.from_user.username, 23, cursor, db)
    elif num == '5':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('Закончить')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Введите никнеймы экспертов, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                         reply_markup=keyboard)
        username = "@" + call.from_user.username
        SetState(username, 221, cursor, db)
    elif num == '4':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + call.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 23)
def edit_status(message):
    status = message.text
    ChangeStatusProject(status, GetCurrProject('@' + message.from_user.username, cursor), cursor, db)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    new_project = "Создать новый проект"
    edit_project = "Редактировать проект"
    list_project = "Список проектов"
    exit = "Назад"
    flag = True
    if isRang(GetRangs('@' + message.from_user.username, cursor), [9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
        keyboard.add(edit_project)
    keyboard.add(list_project)
    keyboard.add(exit)
    SetState('@' + message.from_user.username, 6, cursor, db)
    bot.send_message(message.chat.id, "Статус изменен. Выберите дальнейшее действие", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('delete'))
def editing11(call):
    if (call.data[-1] == '%'):
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + call.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + call.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')
    else:
        nick_and_id = call.data[7:]
        words = nick_and_id.split('*')
        nick = words[0]
        id = words[1]
        DeleteUserFromProject(nick, id, cursor, db)
        members = GetMembersOfProject(id, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for member in members:
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=member[0], callback_data='delete_' + member[0] + '*' + str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='delete_%'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите курсанта из списка участников', reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 22)
def editing2(message):
    nick = message.text
    if (nick[0] != '@'):
        nick = "@" + nick
    if (nick == '@Закончить'):
        SetState('@' + message.from_user.username, 6, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id, 'Изменения приняты. Выберите дальнейшее действие', reply_markup=keyboard)
    elif (IsUserInDB(nick, cursor, db)):
        if isRang(GetRangs(nick, cursor), [2, 3, 4]):
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хипстер', callback_data='adding_2' + nick))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хастлер', callback_data='adding_3' + nick))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хакер', callback_data='adding_4' + nick))
            bot.send_message(message.chat.id, 'Какова его роль в проекте?', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Это не курсант, попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 221)
def editing2_1(message):
    nick = message.text
    if (nick[0] != '@'):
        nick = "@" + nick
    if (nick == '@Закончить'):
        SetState('@' + message.from_user.username, 6, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id, 'Изменения приняты. Выберите дальнейшее действие', reply_markup=keyboard)
    elif (IsUserInDB(nick, cursor, db)):
        if isRang(GetRangs(nick, cursor), [10]):
            AddExpertToProject(GetCurrProject('@' + message.from_user.username, cursor),nick,cursor,db)
            bot.send_message(message.chat.id, 'Эксперт добавлен')
            bot.send_message(GetChatId(nick, cursor),
                             GetName('@' + message.from_user.username, cursor) + ' добавил вас в проект "' +
                             GetProjectTitle(GetCurrProject('@' + message.from_user.username, cursor), cursor) + '"')
        else:
            bot.send_message(message.chat.id, 'Это не эксперт, попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('adding'))
def editing3(call):
    role = call.data[7]
    nick = call.data[8:]
    AddToProject(GetCurrProject('@' + call.from_user.username, cursor), nick, role, cursor, db)
    bot.send_message(GetChatId(nick,cursor),GetName('@'+call.from_user.username,cursor)+' добавил вас в проект "'+
                     GetProjectTitle(GetCurrProject('@' + call.from_user.username, cursor),cursor)+'"')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Принято")


project_info = {}


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 21)
def new_project2(message):
    project_info['name'] = message.text
    bot.send_message(message.chat.id, 'Выберите лидера команды из числа курсантов и введите его никнейм')
    SetState("@" + message.from_user.username, 210, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 210)
def new_project21(message):
    nick = message.text
    if (nick[0] != '@'):
        nick = "@" + nick
    if (IsUserInDB(nick, cursor, db)):
        if isRang(GetRangs(nick, cursor), [2, 3, 4]):
            project_info['leader'] = nick
            keyboard = telebot.types.InlineKeyboardMarkup()
            first = telebot.types.InlineKeyboardButton(text='Учебный', callback_data='type_1')
            second = telebot.types.InlineKeyboardButton(text='Рабочий', callback_data='type_2')
            keyboard.add(first)
            keyboard.add(second)
            bot.send_message(message.chat.id, 'Выберите тип проекта:', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Это не курсант, попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе')


experts = []


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('type'))
def new_project3(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Веберите тип проекта:")
    num = call.data[-1]
    project_info['type'] = num
    #experts.append('@' + call.from_user.username)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('Закончить')
    bot.send_message(call.message.chat.id,
                     'Введите никнеймы экспертов',
                     #'Так как вы инициировали проект, вы являетесь его главным экспертом.Если вы хотите добавить еще экспертов, введите их никнеймы, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                     reply_markup=keyboard)
    SetState("@" + call.from_user.username, 212, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 212)
def new_project4(message):
    nick = message.text
    if (nick == 'Закончить'):
        project_info['experts'] = experts
        SetState("@" + message.from_user.username, 6, cursor, db)
        CreateProject(project_info, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead('@' + message.from_user.username, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id,
                         'Проект "' + project_info['name'] + '" успешно создан. Выберите дальнейшее действие',
                         reply_markup=keyboard)
    else:
        if (nick[0] != '@'):
            nick = "@" + nick
        if (IsUserInDB(nick, cursor, db)):
            if isRang(GetRangs(nick, cursor), [6, 10]):
                experts.append(nick)
                bot.send_message(message.chat.id, "Принято")
            else:
                bot.send_message(message.chat.id, "Этот пользователь не может быть экспертом")
        else:
            bot.send_message(message.chat.id, "Такого пользователя нет в базе")