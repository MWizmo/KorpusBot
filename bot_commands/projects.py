# -*- coding: utf-8 -*-
from db_commands.db_projects import *
from db_commands.db_users import *
from db_commands.db_profile import *
import telebot
from config import bot, db, cursor, get_keyboard, isRang


def projectsMenu(message):
    if message.chat.type == 'private':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(message.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if IsUserTeamlead(message.from_user.id, cursor) and flag:
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')


def project_switch(message, flag):
    if flag == 1:
        bot.send_message(message.chat.id, 'Введите название проекта')
        SetState(message.from_user.id, 21, cursor, db)
    elif flag == 2:
        projects = GetProjects(message.from_user.id, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        if len(projects) != 0:
            for i in range(0, len(projects)):
                keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],
                                                                callback_data='edit_project_' + str(projects[i][1])))
            bot.send_message(message.chat.id, 'Доступные для редактирования проекты', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Доступных для редактирования проектов нет',
                             reply_markup=get_keyboard(message.from_user.id))
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
                             reply_markup=get_keyboard(message.from_user.id))
    elif flag == 4:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, 'Работа с проектами завершена',
                         reply_markup=get_keyboard(message.from_user.id))


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
    if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if IsUserTeamlead(call.from_user.id, cursor) and flag:
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
    SetCurrProject(id, call.from_user.id, cursor, db)
    num = call.data[16]
    if num == '1':
        keyboard = telebot.types.InlineKeyboardMarkup()
        #keyboard.add('Закончить')
        users = GetListOfUsers(cursor)
        for user in users:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0], cursor), callback_data='addmember_'+str(user[0])+'_'+str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='<Закончить>', callback_data='addmember_finish_1'))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Выберите участников команды.',
                         reply_markup=keyboard)
        #username = call.from_user.id
        #SetState(username, 22, cursor, db)
    elif num == '2':
        members = GetMembersOfProject(id, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for member in members:
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=GetName(member[0],cursor), callback_data='delete_' + str(member[0]) + '*' + str(id)))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='delete_%'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите курсанта из списка участников', reply_markup=keyboard)
    elif num == '3':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Исследование рынка', callback_data='status_'+str(id)+'_1'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Разработка MVP', callback_data='status_' + str(id)+'_2'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Развитие проекта', callback_data='status_' + str(id)+'_3'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Завершен', callback_data='status_' + str(id)+'_4'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Закрыт', callback_data='status_' + str(id)+'_5'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите новый статус проекта', reply_markup=keyboard)
        #SetCurrProject(id, call.from_user.id, cursor, db)
        #SetState(call.from_user.id, 23, cursor, db)
    elif num == '5':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('Закончить')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        users = GetListOfUsers(cursor)
        experts = list()
        for user in users:
            if isRang(GetRangs(user[0], cursor), [10]):
                experts.append(user)
        if len(experts):
            keyboard = telebot.types.InlineKeyboardMarkup()
            for expert in experts:
                keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(expert[0], cursor),
                                                                callback_data='addexpert_' + str(expert[0])))
            keyboard.add(telebot.types.InlineKeyboardButton(text='<Закончить>', callback_data='addexpert_finish'))
            bot.send_message(call.message.chat.id,
                             'Выберите экспертов', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             'В данное время нет свободных экспертов')
    elif num == '4':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if IsUserTeamlead(call.from_user.id, cursor) and flag:
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Вкладка <b>"Проекты"</b>', reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('status'))
def editing_status(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    id = call.data.split('_')[1]
    status = call.data.split('_')[2]
    if status == '1':
        status = 'Исследование рынка'
    elif status == '2':
        status = 'Разработка MVP'
    elif status == '3':
        status = 'Развитие проекта'
    elif status == '4':
        status = 'Завершен'
    elif status == '5':
        status = 'Закрыт'
    ChangeStatusProject(status, id, cursor, db)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    new_project = "Создать новый проект"
    edit_project = "Редактировать проект"
    list_project = "Список проектов"
    exit = "Назад"
    flag = True
    if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
        keyboard.add(new_project)
        keyboard.add(edit_project)
        flag = False
    if IsUserTeamlead(call.from_user.id, cursor) and flag:
        keyboard.add(edit_project)
    keyboard.add(list_project)
    keyboard.add(exit)
    #SetState(message.from_user.id, 6, cursor, db)
    bot.send_message(call.message.chat.id, "Статус изменен. Выберите дальнейшее действие", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('delete'))
def editing11(call):
    if call.data[-1] == '%':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if IsUserTeamlead(call.from_user.id, cursor) and flag:
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


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('addmember'))
def editing2(call):
    member = call.data.split('_')[1]
    id = call.data.split('_')[2]
    if member == 'finish':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        SetState(call.from_user.id, 6, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if IsUserTeamlead(call.from_user.id, cursor) and flag:
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(call.message.chat.id, 'Изменения приняты. Выберите дальнейшее действие', reply_markup=keyboard)
    else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хипстер', callback_data='adding_2_' + str(member)+'_'+str(id)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хастлер', callback_data='adding_3_' + str(member)+'_'+str(id)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Хакер', callback_data='adding_4_' + str(member)+'_'+str(id)))
            bot.send_message(call.message.chat.id, 'Какова его роль в проекте?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('addexpert'))
def editing2_1(call):
    expert = call.data.split('_')[1]
    if expert == 'finish':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        #SetState(message.from_user.id, 6, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if IsUserTeamlead(call.from_user.id, cursor) and flag:
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(call.message.chat.id, 'Изменения приняты. Выберите дальнейшее действие', reply_markup=keyboard)
    else:
            AddExpertToProject(GetCurrProject(call.from_user.id, cursor), expert, cursor, db)
            bot.send_message(call.message.chat.id, 'Эксперт добавлен')
            bot.send_message(GetChatId(expert, cursor),
                             GetName(call.from_user.id, cursor) + ' добавил вас в проект "' +
                             GetProjectTitle(GetCurrProject(call.from_user.id, cursor), cursor) + '"')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('adding'))
def editing3(call):
    role = call.data.split('_')[1]
    member = call.data.split('_')[2]
    project = call.data.split('_')[3]
    AddToProject(project, member, role, cursor, db)
    bot.send_message(GetChatId(member, cursor),
                     GetName(call.from_user.id, cursor) + ' добавил вас в проект "' +
                     GetProjectTitle(GetCurrProject(call.from_user.id, cursor), cursor) + '"')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Принято")


project_info = {}


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 21)
def new_project2(message):
    project_info['name'] = message.text
    users = GetListOfUsers(cursor)
    students = list()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
            students.append(user)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for student in students:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(student[0],cursor), callback_data='chooseteamlead_' + str(student[0])))
    bot.send_message(message.chat.id, 'Выберите лидера команды из числа курсантов', reply_markup=keyboard)
    #SetState(message.from_user.id, 210, cursor, db)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('chooseteamlead_'))
def new_project21(call):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            user = call.data.split('_')[1]
            project_info['leader'] = user
            keyboard = telebot.types.InlineKeyboardMarkup()
            first = telebot.types.InlineKeyboardButton(text='Учебный', callback_data='type_1')
            second = telebot.types.InlineKeyboardButton(text='Рабочий', callback_data='type_2')
            keyboard.add(first)
            keyboard.add(second)
            bot.send_message(call.message.chat.id, 'Выберите тип проекта:', reply_markup=keyboard)


experts = []


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('type'))
def new_project3(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Выберите тип проекта:")
    num = call.data[-1]
    project_info['type'] = num
    # experts.append(call.from_user.id)
    users = GetListOfUsers(cursor)
    experts = list()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [10]):
            experts.append(user)
    if len(experts):
        keyboard = telebot.types.InlineKeyboardMarkup()
        for expert in experts:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(expert[0], cursor),
                                                            callback_data='chooseexpert_' + str(expert[0])))
        keyboard.add(telebot.types.InlineKeyboardButton(text='<Закончить>', callback_data='chooseexpert_finish'))
        bot.send_message(call.message.chat.id,
                         'Выберите экспертов',
                         # 'Так как вы инициировали проект, вы являетесь его главным экспертом.Если вы хотите добавить еще экспертов, введите их никнеймы, каждый отдельным сообщением. Для завершения нажмите на кнопку.',
                         reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id,
                         'В данное время нет свободных экспертов')
        project_info['experts'] = []
        SetState(call.from_user.id, 6, cursor, db)
        CreateProject(project_info, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead(call.from_user.id, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(call.message.chat.id,
                         'Проект "' + project_info['name'] + '" успешно создан. Выберите дальнейшее действие',
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('chooseexpert'))
def new_project4(call):
    expert = call.data.split('_')[1]
    if expert == 'finish':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        project_info['experts'] = experts
        SetState(call.from_user.id, 6, cursor, db)
        CreateProject(project_info, cursor, db)
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        new_project = "Создать новый проект"
        edit_project = "Редактировать проект"
        list_project = "Список проектов"
        exit = "Назад"
        flag = True
        if isRang(GetRangs(call.from_user.id, cursor), [7, 9, 10]):
            keyboard.add(new_project)
            keyboard.add(edit_project)
            flag = False
        if (IsUserTeamlead(call.from_user.id, cursor) and flag):
            keyboard.add(edit_project)
        keyboard.add(list_project)
        keyboard.add(exit)
        bot.send_message(call.message.chat.id,
                         'Проект "' + project_info['name'] + '" успешно создан. Выберите дальнейшее действие',
                         reply_markup=keyboard)
    else:
        experts.append(expert)
        SetState(call.from_user.id, 6, cursor, db)
        bot.send_message(call.message.chat.id, "Принято")
