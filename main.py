# -*- coding: utf-8 -*-
import telebot
from db_commands import *
import sqlite3
import config
from config import bot, db, cursor, get_keyboard, isRang
from emoji import emojize
import cherrypy
from telegram.ext.dispatcher import run_async
import re
import datetime
from cherrypy.process.plugins import Daemonizer


d = Daemonizer(cherrypy.engine)


WEBHOOK_HOST = '195.201.138.7'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '195.201.138.7'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)


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


def reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Введите свое полное имя")
    SetState("@" + message.from_user.username, 1, cursor, db)


def red_profile(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Имя', callback_data='profile_1'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Телефон', callback_data='profile_2'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Электронный адрес', callback_data='profile_3'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Фото', callback_data='profile_4'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Адрес Etherium-кошелька', callback_data='profile_6'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='profile_5'))
    bot.send_message(message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('profile'))
def redacting_profile(call):
    if call.data[-1] == '1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новое имя')
        SetState('@' + call.from_user.username, 41, cursor, db)
    elif call.data[-1] == '2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый телефон')
        SetState('@' + call.from_user.username, 42, cursor, db)
    elif call.data[-1] == '3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый электронный адрес')
        SetState('@' + call.from_user.username, 43, cursor, db)
    elif call.data[-1] == '4':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Загрузите новое фото')
        SetState('@' + call.from_user.username, 44, cursor, db)
    elif call.data[-1] == '6':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый адрес кошелька')
        SetState('@' + call.from_user.username, 45, cursor, db)
    elif call.data[-1] == '5':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Редактирование окончено',
                         reply_markup=get_keyboard('@' + call.from_user.username))
        SetState('@' + call.from_user.username, 6, cursor, db)


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
    if re.fullmatch(r'\+7\d{10}', phone) or re.fullmatch(r'8\d{10}', phone):
        UpdatePhone("@" + message.from_user.username, phone, cursor, db)
        bot.send_message(message.chat.id, text='Телефон изменен')
        SetState("@" + message.from_user.username, 6, cursor, db)
        red_profile(message)
    else:
        bot.send_message(message.chat.id, 'Введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 43)
def user_redacting_email(message):
    email = message.text
    if re.fullmatch(r'\w+@[a-z]+\.[a-z]{,4}', email):
        UpdateEmail("@" + message.from_user.username, email, cursor, db)
        bot.send_message(message.chat.id, text='Электронный адрес изменен')
        SetState("@" + message.from_user.username, 6, cursor, db)
        red_profile(message)
    else:
        bot.send_message(message.chat.id, 'Введите адрес электронной почты в формате *@*.*')


@bot.message_handler(content_types=["photo"],
                     func=lambda message: GetState(message.from_user.username, cursor, db) == 44)
def user_redacting_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    UpdatePhoto("@" + message.from_user.username, photo, cursor, db)
    bot.send_message(message.chat.id, text='Фото изменено')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 45)
def user_redacting_wallet(message):
    wallet = message.text
    UpdateWallet("@" + message.from_user.username, wallet, cursor, db)
    bot.send_message(message.chat.id, text='Адрес кошелька изменен')
    SetState("@" + message.from_user.username, 6, cursor, db)
    red_profile(message)

def start_voting(message):
    if (message.chat.type == 'private'):
        if isRang(GetRangs('@' + message.from_user.username, cursor), [2,3,4]):
            projects = GetProjects("@" + message.from_user.username, cursor)
            keyboard = telebot.types.InlineKeyboardMarkup()
            if len(projects) != 0:
                for i in range(0, len(projects)):
                    keyboard.add(telebot.types.InlineKeyboardButton(text=projects[i][0],
                                                                    callback_data='vote_project%' + str(projects[i][1])))
                bot.send_message(message.chat.id, 'В рамках какого проекта проводится оценка нематериального вклада?', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'Нет доступных проектов для оценивания нематериального вклада')
        # keyboard=telebot.types.InlineKeyboardMarkup()
        # a=GetRangs('@' + message.from_user.username, cursor)
        # if isRang(GetRangs('@' + message.from_user.username, cursor), [2]):
        #     keyboard.add(telebot.types.InlineKeyboardButton(text='Оценить других курсантов по оси отношений',callback_data='vote_choose_1'))
        # # elif isRang(GetRangs('@' + message.from_user.username, cursor), [3]) and IsInProject(
        # #         '@' + message.from_user.username, cursor):
        # #     keyboard = telebot.types.InlineKeyboardMarkup()
        # #     projects = GetProjects('@' + message.from_user.username, cursor)
        # #     for project in projects:
        # #         keyboard.add(
        # #             telebot.types.InlineKeyboardButton(project[0], callback_data='project_decision_' + str(project[1])))
        # #     bot.send_message(message.chat.id, 'Выберите проект', reply_markup=keyboard)
        # if isRang(GetRangs('@' + message.from_user.username, cursor), [6]):
        #     keyboard.add(telebot.types.InlineKeyboardButton(text='Оценить курсантов по оси дела как преподаватель', callback_data='vote_choose_2'))
        # if (isRang(GetRangs('@' + message.from_user.username, cursor), [5, 7])):
        #     keyboard.add(telebot.types.InlineKeyboardButton(text='Оценить курсантов по оси отношений', callback_data='vote_choose_3'))
        # if (isRang(GetRangs('@' + message.from_user.username, cursor), [10])):
        #     keyboard.add(telebot.types.InlineKeyboardButton(text='Оценить курсантов по оси дела как эксперт', callback_data='vote_choose_4'))
        # if (GetAuthority('@' + message.from_user.username, cursor) > 0):
        #     keyboard.add(telebot.types.InlineKeyboardButton(text='Оценить курсантов по оси власти',callback_data='vote_choose_5'))
        #
        # if len(keyboard.keyboard)>0:
        #     bot.send_message(message.chat.id, "Веберите опцию для голосования", reply_markup=keyboard)
        # else:
        #     bot.send_message(message.chat.id, "Вы пока не можете оценивать нематериальный вклад",
        #                      reply_markup=get_keyboard('@' + message.from_user.username))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('vote_project'))
def voting(call):
    bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
    id = call.data.split('%')[1]
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось отношений',callback_data='vote_in_prj%'+str(id)+'%1'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось дела', callback_data='vote_in_prj%' + str(id) + '%2'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось власти', callback_data='vote_in_prj%' + str(id) + '%3'))
    bot.send_message(call.message.chat.id,'По какой оси проводится оценка?',reply_markup=keyboard)
    # if call.data[-1]=='1':
    #     if MayCoursantVote(cursor):
    #         SetCurrentFighterVoting('@' + call.from_user.username, 0, cursor, db)
    #         users = GetListOfUsers(cursor)
    #         config.fighters_list = list()
    #         for user in users:
    #             if isRang(GetRangs(user[0], cursor), [2, 3]) and user[0] != '@' + call.from_user.username:
    #                 config.fighters_list.append(user)
    #         if len(config.fighters_list) != 0:
    #             config.fighters_num = len(config.fighters_list)
    #             info = []
    #             for i in range(0, 3): info.append(0)
    #             config.fighters_marks['@' + call.from_user.username] = info
    #             bot.send_message(call.message.chat.id,
    #                              'Оценка нематериального вклада.\nОсь отношений \nКурсант: ' +
    #                              GetName(config.fighters_list[
    #                                  GetCurrentFighterVoting('@' + call.from_user.username, cursor)][0],cursor) +
    #                              '\nЛичностное развитие: - \nПонятность: - \nЭнергия: - ',
    #                              reply_markup=config.ChooseKeyboardForRelations(
    #                                  '@' + call.from_user.username, cursor))
    #         else:
    #             bot.send_message(call.message.chat.id, 'Список курсантов пуст',
    #                              reply_markup=get_keyboard('@' + call.from_user.username))
    #     else:
    #         bot.send_message(call.message.chat.id, 'Тьютор пока не запустил голосование курсантов',
    #                          reply_markup=get_keyboard('@' + call.from_user.username))
    # elif call.data[-1]=='2' or call.data[-1]=='4':
    #     config.current_fighter_for_business = 0
    #     users = GetListOfUsers(cursor)
    #     config.fighters_list = list()
    #     for user in users:
    #         if isRang(GetRangs(user[0], cursor), [2, 3]) and user[0] != '@' + call.from_user.username:
    #             config.fighters_list.append(user)
    #     config.fighters_num = len(config.fighters_list)
    #     config.business_marks = [0, 0, 0]
    #     bot.send_message(call.message.chat.id, 'Оценка нематериального вклада.\nОсь дела \nКурсант: ' +
    #                      GetName(config.fighters_list[0][0],cursor) +
    #                      '\nДвижение : - \nЗавершенность: - \nПодтвержденность средой: -',
    #                      reply_markup=config.ChooseKeyboardForBusiness())
    # elif call.data[-1]=='3':
    #     SetCurrentFighterVoting('@' + call.from_user.username, 0, cursor, db)
    #     users = GetListOfUsers(cursor)
    #     config.fighters_list = list()
    #     for user in users:
    #         if isRang(GetRangs(user[0], cursor), [2, 3]) and user[0] != '@' + call.from_user.username:
    #             config.fighters_list.append(user)
    #     if len(config.fighters_list) != 0:
    #         config.fighters_num = len(config.fighters_list)
    #         info = []
    #         for i in range(0, 3): info.append(0)
    #         config.fighters_marks['@' + call.from_user.username] = info
    #         bot.send_message(call.message.chat.id,
    #                          'Оценка нематериального вклада.\nОсь отношений \nКурсант: ' +
    #                          GetName(config.fighters_list[
    #                                      GetCurrentFighterVoting('@' + call.from_user.username, cursor)][0], cursor) +
    #                          '\nЛичностное развитие: - \nПонятность: - \nЭнергия: - ',
    #                          reply_markup=config.ChooseKeyboardForRelations(
    #                              '@' + call.from_user.username, cursor))
    # elif call.data[-1]=='4':
    #     config.current_fighter_for_business = 0
    #     users = GetListOfUsers(cursor)
    #     config.second_flow_list = list()
    #     for user in users:
    #         if isRang(GetRangs(user[0], cursor), [2,3]) and user[0] != '@' + call.from_user.username:
    #             config.second_flow_list.append(user)
    #     config.second_flow_num = len(config.second_flow_list)
    #     config.business_marks = [0, 0, 0]
    #     bot.send_message(call.message.chat.id, 'Оценка нематериального вклада.\nОсь дела \nКурсант: ' +
    #                      GetName(config.second_flow_list[0][0],cursor) +
    #                      '\nДвижение : - \nЗавершенность: - \nПодтвержденность средой: -',
    #                      reply_markup=config.ChooseKeyboardForBusiness())
    # elif call.data[-1]=='5':
    #     config.current_fighter_for_authority = 0
    #     users = GetListOfUsers(cursor)
    #     config.fighters_list = list()
    #     for user in users:
    #         if isRang(GetRangs(user[0], cursor), [2,3]) and user[0] != '@' + call.from_user.username:
    #             config.fighters_list.append(user)
    #     config.fighters_num = len(config.fighters_list)
    #     config.authority_first_marks = [0, 0, 0]
    #     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
    #                           text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
    #                                GetName(config.fighters_list[0][0],cursor) +
    #                                '\nСамоуправление: - \nСтратегия: - \nУправляемость: -',
    #                           reply_markup=config.ChooseKeyboardForAuthority())

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('vote_in_prj'))
def voting_starts(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    id = call.data.split('%')[1]
    axis = call.data.split('%')[2]
    if axis=='1':
        config.project_relation_marks[call.from_user.username] = [0, 0, 0, id]
        bot.send_message(call.message.chat.id,
                              'Оценка нематериального вклада.\nОсь отношений \nКурсант: ' + GetName('@'+call.from_user.username,cursor) +
                                     '\nЛичностное развитие: - \nПонятность: - \nЭнергия: - ',
                                     reply_markup=config.ChooseKeyboardForRelations())
    elif axis=='2':
        config.project_business_marks[call.from_user.username] = [0, 0, 0, id]
        bot.send_message(call.message.chat.id, 'Оценка нематериального вклада.\nОсь дела \nКурсант: ' +
                             GetName('@'+call.from_user.username,cursor) +
                             '\nДвижение : - \nЗавершенность: - \nПодтвержденность средой: -',
                             reply_markup=config.ChooseKeyboardForBusiness())
    elif axis=='3':
        config.project_authority_marks[call.from_user.username] = [0, 0, 0, id]
        bot.send_message(call.message.chat.id, text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
                                    GetName('@'+call.from_user.username,cursor) +
                                    '\nСамоуправление: - \nСтратегия: - \nУправляемость: -',
                                    reply_markup=config.ChooseKeyboardForAuthority())


def put_sign(num):
    if num==0:
        return '-'
    else:
        return '+'

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('relations'))
def fighters_vote(call):
    if call.data[-1] != "5":
        if call.data[-1] == "1":
            config.project_relation_marks[call.from_user.username][0] = 1 if \
            config.project_relation_marks[call.from_user.username][0] == 0 else 0
        elif call.data[-1] == "2":
            config.project_relation_marks[call.from_user.username][1] = 1 if \
            config.project_relation_marks[call.from_user.username][1] == 0 else 0
        elif call.data[-1] == "3":
            config.project_relation_marks[call.from_user.username][2] = 1 if \
            config.project_relation_marks[call.from_user.username][2] == 0 else 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь отношений\nКурсант: ' +
                                   GetName('@' + call.from_user.username,cursor) +
                                   '\nЛичностное развитие: ' + put_sign(config.project_relation_marks[call.from_user.username][0]) +
                                   '\nПонятность: ' + put_sign(config.project_relation_marks[ call.from_user.username][1]) +
                                   '\nЭнергия: ' + put_sign(config.project_relation_marks[call.from_user.username][2]),
                              reply_markup=config.ChooseKeyboardForRelations())
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        id = config.project_relation_marks[call.from_user.username][3]
        project_members = GetMembersOfProject(id,cursor)
        AddMark('@' + call.from_user.username, config.project_relation_marks[call.from_user.username][:3], 1,len(project_members)-1, cursor,db)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%'+str(id)+'%@'+call.from_user.username+'%1%1'),
                     telebot.types.InlineKeyboardButton(text='Не согласен',callback_data='decide_vote%' + str(id) + '%@' + call.from_user.username + '%2%1'))
        for member in project_members:
            if member[0]!='@'+call.from_user.username:
                bot.send_message(GetChatId(member[0],cursor),'Курсант '+GetName('@'+call.from_user.username,cursor)+
				' оценил себя по оси отношений в рамках проекта "' + GetProjectTitle(id,cursor) +
                                 '". Вот его оценки:\n Личностное развитие: ' +
                                 str(config.project_relation_marks[call.from_user.username][0]) +
                                 '\n Понятность: ' + str(config.project_relation_marks[ call.from_user.username][1]) +
                                 '\n Энергия: ' + str(config.project_relation_marks[call.from_user.username][2]) +'\nВы согласны с этими оценками?',
                                 reply_markup=keyboard)
                StartEvaluateInProject(int(id),'@'+call.from_user.username,1,config.project_relation_marks[call.from_user.username][:3],member,cursor,db)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('business'))
def educator_votes(call):
    if call.data[-1] != '5':
        if call.data[-1] == '1':
            config.project_business_marks[call.from_user.username][0] = 1 \
                if config.project_business_marks[call.from_user.username][0] == 0 else 0
        if call.data[-1] == '2':
            config.project_business_marks[call.from_user.username][1] = 1 \
                if config.project_business_marks[call.from_user.username][1] == 0 else 0
        if call.data[-1] == '3':
            config.project_business_marks[call.from_user.username][2] = 1 \
                if config.project_business_marks[call.from_user.username][2] == 0 else 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь дела \nКурсант: ' +
                                   GetName('@' + call.from_user.username,cursor) +
                                   '\nДвижение: ' + put_sign(config.project_business_marks[call.from_user.username][0]) + '\nЗавершенность: ' +
                                   put_sign(config.project_business_marks[call.from_user.username][1]) +
                                   '\nПодтверждение средой: ' + put_sign(config.project_business_marks[call.from_user.username][2]),
                              reply_markup=config.ChooseKeyboardForBusiness())
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        id = config.project_business_marks[call.from_user.username][3]
        project_members = GetMembersOfProject(id, cursor)
        AddMark('@' + call.from_user.username, config.project_business_marks[call.from_user.username][:3], 2,
                len(project_members)-1, cursor, db)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%' + str(
            id) + '%@' + call.from_user.username + '%1%2'),
                     telebot.types.InlineKeyboardButton(text='Не согласен', callback_data='decide_vote%' + str(
                         id) + '%@' + call.from_user.username + '%2%2'))
        for member in project_members:
            if member[0]!='@'+call.from_user.username:
                bot.send_message(GetChatId(member[0], cursor), 'Курсант ' + GetName('@' + call.from_user.username, cursor) +
                                 ' оценил себя по оси дела в рамках проекта "' + GetProjectTitle(id,cursor) +
                                 '". Вот его оценки:\n Движение: ' +
                                 str(config.project_business_marks[call.from_user.username][0]) +
                                 '\n Завершенность: ' + str(config.project_business_marks[call.from_user.username][1]) +
                                 '\n Подтверждение средой: ' + 
                                 str(config.project_business_marks[call.from_user.username][2]) + '\nВы согласны с этими оценками?',
                                 reply_markup=keyboard)
                StartEvaluateInProject(int(id), '@' + call.from_user.username, 2,config.project_business_marks[call.from_user.username][:3], member, cursor, db)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('authority'))
def authority_votes1(call):
    if call.data[-1] != '5':
        if call.data[-1] == '1':
            config.project_authority_marks[call.from_user.username][0] = 1 \
                if config.project_authority_marks[call.from_user.username][0] == 0 else 0
        if call.data[-1] == '2':
            config.project_authority_marks[call.from_user.username][1] = 1 \
                if config.project_authority_marks[call.from_user.username][1] == 0 else 0
        if call.data[-1] == '3':
            config.project_authority_marks[call.from_user.username][2] = 1 \
                if config.project_authority_marks[call.from_user.username][2] == 0 else 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
                                   GetName('@'+call.from_user.username,cursor) +
                                   '\nСамоуправление: ' + put_sign(config.project_authority_marks[call.from_user.username][0]) +
                                   '\nСтратегия: ' + put_sign(config.project_authority_marks[call.from_user.username][1]) +
                                   '\nУправляемость: ' + put_sign(config.project_authority_marks[call.from_user.username][2]),
                              reply_markup=config.ChooseKeyboardForAuthority())
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        id = config.project_authority_marks[call.from_user.username][3]
        project_members = GetMembersOfProject(id, cursor)
        AddMark('@' + call.from_user.username, config.project_authority_marks[call.from_user.username][:3], 3,
                len(project_members)-1, cursor, db)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%' + str(
            id) + '%@' + call.from_user.username + '%1%3'),
                     telebot.types.InlineKeyboardButton(text='Не согласен', callback_data='decide_vote%' + str(
                         id) + '%@' + call.from_user.username + '%2%3'))
        for member in project_members:
            if member[0]!='@'+call.from_user.username:
                bot.send_message(GetChatId(member[0], cursor), 'Курсант ' + GetName('@' + call.from_user.username, cursor) +
                                 ' оценил себя по оси власти в рамках проекта "' + GetProjectTitle(id,cursor) +
                                 '". Вот его оценки:\n Самоуправление: ' +
                                 str(config.project_authority_marks[call.from_user.username][0]) +
                                 '\n Стратегия: ' + str(config.project_authority_marks[call.from_user.username][1]) +
                                 '\n Управляемость: ' + 
                                 str(config.project_authority_marks[call.from_user.username][2]) + '\nВы согласны с этими оценками?',
                                 reply_markup=keyboard)
        bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('decide_vote'))
def decide_in_vote(call):
    elems = call.data.split('%')
    project_id = int(elems[1])
    user = elems[2]
    verdict = int(elems[3])
    axis = int(elems[4])
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if verdict == 1:
        answer = EvaluateInProject(project_id, user, axis, '@' + call.from_user.username, 'agree', cursor, db)
        if answer == 1:
            if axis == 1:
                bot.send_message(GetChatId(user,cursor),'Оценки в проекте "'+GetProjectTitle(project_id,cursor)+'" по оси отношений были одобрены')
            elif axis == 2:
                bot.send_message(GetChatId(user, cursor), 'Оценки в проекте "' + GetProjectTitle(project_id,cursor) + '" по оси дела были одобрены')
            elif axis == 3:
                bot.send_message(GetChatId(user, cursor), 'Оценки в проекте "' + GetProjectTitle(project_id,cursor) + '" по оси власти были одобрены')
        bot.send_message(call.message.chat.id, 'Отлично, голос учтен')
    else:
        EvaluateInProject(project_id, user, axis, '@' + call.from_user.username, 'disagree', cursor, db)
        bot.send_message(call.message.chat.id, 'Напишите, с чем и почему вы не согласны')
        if axis == 1:
            SetState('@'+call.from_user.username,81,cursor,db)
        elif axis == 2:
            SetState('@' + call.from_user.username, 82, cursor, db)
        elif axis == 3:
            SetState('@' + call.from_user.username, 83, cursor, db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 81)
def explain1(message):
    explanation = message.text
    id, user = ExplainEvaluationInProject(1,'@'+message.from_user.username,explanation,cursor,db)
    bot.send_message(GetChatId(user,cursor),'Оценки в проекте "'+GetProjectTitle(id,cursor)+
                     '" по оси отношений не были одобрены пользователем '+GetName('@'+message.from_user.username,cursor)+'.\nПричина: '+explanation)
    SetState('@' + message.from_user.username, 6, cursor, db)
    bot.send_message(message.chat.id,'Спасибо за пояснения',reply_markup=get_keyboard('@' + message.from_user.username))

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 82)
def explain2(message):
    explanation = message.text
    id, user = ExplainEvaluationInProject(1, '@' + message.from_user.username, explanation, cursor, db)
    bot.send_message(GetChatId(user, cursor), 'Оценки в проекте "' + GetProjectTitle(id, cursor) +
                     '" по оси дела не были одобрены пользователем ' + GetName('@' + message.from_user.username,
                                                                                    cursor) + '.\nПричина: ' + explanation)
    SetState('@' + message.from_user.username, 6, cursor, db)
    SetState('@' + message.from_user.username, 6, cursor, db)
    bot.send_message(message.chat.id,'Спасибо за пояснения',reply_markup=get_keyboard('@' + message.from_user.username))

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 83)
def explain3(message):
    explanation = message.text
    id, user = ExplainEvaluationInProject(1, '@' + message.from_user.username, explanation, cursor, db)
    bot.send_message(GetChatId(user, cursor), 'Оценки в проекте "' + GetProjectTitle(id, cursor) +
                     '" по оси власти не были одобрены пользователем ' + GetName('@' + message.from_user.username,
                                                                                    cursor) + '.\nПричина: ' + explanation)
    SetState('@' + message.from_user.username, 6, cursor, db)
    SetState('@' + message.from_user.username, 6, cursor, db)
    bot.send_message(message.chat.id,'Спасибо за пояснения',reply_markup=get_keyboard('@' + message.from_user.username))

# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_relations'))
# def tutor_votes(call):
#     if call.data[-1] != "7":
#         if call.data[-1] == "1":
#             config.tutor_marks[0] = 1 if config.tutor_marks[0] == 0 else 0
#         elif call.data[-1] == "2":
#             config.tutor_marks[1] = 1 if config.tutor_marks[1] == 0 else 0
#         elif call.data[-1] == "3":
#             config.tutor_marks[2] = 1 if config.tutor_marks[2] == 0 else 0
#         elif call.data[-1] == "4":
#             config.tutor_marks[3] = 1 if config.tutor_marks[3] == 0 else 0
#         elif call.data[-1] == "5":
#             config.tutor_marks[4] = 1 if config.tutor_marks[4] == 0 else 0
#         elif call.data[-1] == '6':
#             AddMark(config.second_flow_list[config.current_fighter_for_tutor][0], config.tutor_marks, 1, 2, cursor, db)
#             config.current_fighter_for_tutor += 1
#             config.tutor_marks = [0, 0, 0, 0, 0]
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь отношений, второй курс \nКурсант: ' +
#                                    config.second_flow_list[config.current_fighter_for_tutor][0] +
#                                    '\nЧестность: ' + str(config.tutor_marks[0]) + '\nЯсность позиции: ' + str(
#                                   config.tutor_marks[1]) +
#                                    '\nУровень энергии: ' + str(
#                                   config.tutor_marks[2]) + '\nУстойчивость личностного роста: ' + str(
#                                   config.tutor_marks[3]) +
#                                    '\nИнтенсивность личностного роста: ' + str(config.tutor_marks[4]),
#                               reply_markup=config.ChooseKeyboardForSecondFlowRelations())
#     else:
#         AddMark(config.second_flow_list[config.current_fighter_for_tutor][0], config.tutor_marks, 1, 2, cursor, db)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',
#                          reply_markup=get_keyboard('@' + call.from_user.username))
#
#
# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_business'))
# def expert_votes(call):
#     if call.data[-1] != '7':
#         if call.data[-1] == '1':
#             config.expert_marks[0] = 1 if config.expert_marks[0] == 0 else 0
#         elif call.data[-1] == '2':
#             config.expert_marks[1] = 1 if config.expert_marks[1] == 0 else 0
#         elif call.data[-1] == '3':
#             config.expert_marks[2] = 1 if config.expert_marks[2] == 0 else 0
#         elif call.data[-1] == '4':
#             config.expert_marks[3] = 1 if config.expert_marks[3] == 0 else 0
#         elif call.data[-1] == '5':
#             config.expert_marks[4] = 1 if config.expert_marks[4] == 0 else 0
#         elif call.data[-1] == '6':
#             AddMark(config.second_flow_list[config.current_fighter_for_expert][0], config.expert_marks, 2, 2, cursor,
#                     db)
#             config.current_fighter_for_expert += 1
#             config.expert_marks = [0, 0, 0, 0, 0]
#
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь дела, второй курс \nКурсант: ' +
#                                    config.second_flow_list[config.current_fighter_for_expert][0] +
#                                    '\nДвижение к цели: ' + str(config.expert_marks[0]) + ' \nРезультативность: ' + str(
#                                   config.expert_marks[1]) +
#                                    '\nАдекватность картины мира: ' + str(config.expert_marks[2]) +
#                                    '\nВедение переговоров с внутренними и внешними референтными группами: ' + str(
#                                   config.expert_marks[3]) +
#                                    '\n Эффективность работы в команде: ' + str(config.expert_marks[4]),
#                               reply_markup=config.ChooseKeyboardForSecondFlowBusiness())
#     else:
#         AddMark(config.second_flow_list[config.current_fighter_for_expert][0], config.expert_marks, 2, 2, cursor, db)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',
#                          reply_markup=get_keyboard('@' + call.from_user.username))
#
#
# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_projects'))
# def voting_in_project(call):
#     if call.data[-1] != '7':
#         if call.data[-1] == '1':
#             config.project_marks[0] = 1 if config.project_marks[0] == 0 else 0
#         elif call.data[-1] == '2':
#             config.project_marks[1] = 1 if config.project_marks[1] == 0 else 0
#         elif call.data[-1] == '3':
#             config.project_marks[2] = 1 if config.project_marks[2] == 0 else 0
#         elif call.data[-1] == '4':
#             config.project_marks[3] = 1 if config.project_marks[3] == 0 else 0
#         elif call.data[-1] == '5':
#             config.project_marks[4] = 1 if config.project_marks[4] == 0 else 0
#         elif call.data[-1] == '6':
#             AddMarkFromProject(config.project_members[config.current_project_member][0], config.project_marks, 2, 2,
#                                cursor, db)
#             config.current_project_member += 1
#             config.project_marks = [0, 0, 0, 0, 0]
#
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь дела, второй курс.\nПроект: ' + config.current_project + ' \nКурсант: ' +
#                                    config.project_members[config.current_project_member][0] +
#                                    '\nДвижение к цели: ' + str(config.project_marks[0]) + ' \nРезультативность: ' + str(
#                                   config.project_marks[1]) +
#                                    '\nАдекватность картины мира: ' + str(config.project_marks[2]) +
#                                    '\nВедение переговоров с внутренними и внешними референтными группами: ' + str(
#                                   config.project_marks[3]) +
#                                    '\n Эффективность работы в команде: ' + str(config.project_marks[4]),
#                               reply_markup=config.ChooseKeyboardForSecondFlowProjectBusiness())
#     else:
#         AddMarkFromProject(config.project_members[config.current_project_member][0], config.project_marks, 2, 2, cursor,
#                            db)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',
#                          reply_markup=get_keyboard('@' + call.from_user.username))
#
#
# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('second_flow_authority'))
# def authority_votes2(call):
#     if call.data[-1] != '7':
#         if call.data[-1] == '1':
#             config.authority_second_marks[0] = 1 if config.authority_second_marks[0] == 0 else 0
#         if call.data[-1] == '2':
#             config.authority_second_marks[1] = 1 if config.authority_second_marks[1] == 0 else 0
#         if call.data[-1] == '3':
#             config.authority_second_marks[2] = 1 if config.authority_second_marks[2] == 0 else 0
#         if call.data[-1] == '4':
#             config.authority_second_marks[3] = 1 if config.authority_second_marks[3] == 0 else 0
#         if call.data[-1] == '5':
#             config.authority_second_marks[4] = 1 if config.authority_second_marks[4] == 0 else 0
#         if call.data[-1] == '6':
#             AddMark(config.second_flow_list[config.current_second_flow_for_authority][0], config.authority_second_marks,
#                     3, 2, cursor, db)
#             config.current_second_flow_for_authority += 1
#             config.authority_second_marks = [0, 0, 0, 0, 0]
#
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
#                                    config.second_flow_list[config.current_second_flow_for_authority][0] +
#                                    '\nРазвитие парадигмы децентрализации:' + str(config.authority_second_marks[0]) +
#                                    '\nСтратегическое развитие сообщества:' + str(config.authority_second_marks[1]) +
#                                    '\nУправление ресурсами:' + str(config.authority_second_marks[2]) +
#                                    '\nУправляемость проектов:' + str(config.authority_second_marks[3]) +
#                                    '\nПроф. доверие:' + str(config.authority_second_marks[4]),
#                               reply_markup=config.ChooseKeyboardForSecondFlowAuthority())
#     else:
#         AddMark(config.second_flow_list[config.current_second_flow_for_authority][0], config.authority_second_marks, 3,
#                 2, cursor, db)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',
#                          reply_markup=get_keyboard('@' + call.from_user.username))


def get_profile(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [2, 3, 4, 5, 6, 7, 8, 9, 10]):
            profile = GetProfile('@' + message.from_user.username, cursor)
            if profile[0] != None:
                string = 'Пользователь: ' + profile[0]
                string += "\nФото: "
                bot.send_message(message.chat.id, string)
                try:
                    bot.send_photo(message.chat.id, profile[3])
                except telebot.apihelper.ApiException:
                    bot.send_message(message.chat.id, 'Фото недоступно')
                string = "Телефон: " + str(profile[1])
                string = string + "\nЭлектронная почта: " + profile[2]
                try:
                    string = string + "\nДата регистрации: " + profile[5]
                    string = string + '\nАвторитет: ' + str(profile[4])
                    if profile[6] == None:
                        string = string + '\nСумма оценок в текущем месяце: 0'
                    else:
                        string = string + '\nСумма оценок в текущем месяце: ' + str(profile[6])
                    if profile[7] != None:
                        string = string + '\nДосье: ' + profile[7]
                    wallet = GetWallet('@' + message.from_user.username, cursor)
                    if wallet != 'wallet':
                        string = string + '\nEtherium-кошелек:' + wallet
                    try:
                        string = string +'\nТокены вклада: '+str(GetContributionTokens('@' + message.from_user.username, cursor))
                        string = string + '\nТокены инвестиций: ' + str(GetInvestmentTokens('@' + message.from_user.username, cursor))
                    except:
                        print("Fix it 2")
                except:
                    print("Fix it")
                string = string + '\nРоли в системе: '
                rangs = GetRangs('@' + message.from_user.username, cursor)
                for rang in rangs:
                    string = string + GetTitleOfRang(rang, cursor) + ', '
                string = string[:len(string) - 2]
                bot.send_message(message.chat.id, string,
                                 reply_markup=get_keyboard('@' + message.from_user.username))
            else:
                bot.send_message(message.chat.id, "Ой, анкета еще не заполнена",
                                 reply_markup=get_keyboard('@' + message.from_user.username))
            SetState("@" + message.from_user.username, 6, cursor, db)



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


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 1)
def user_entering_fio(message):
    if IsAbit('@' + message.from_user.username, cursor, db):
        name = message.text
        bot.send_message(message.chat.id, "Всё, кажется запомнил. Теперь напиши свой номер телефона, он мне пригодится")
        SetState("@" + message.from_user.username, 2, cursor, db)
    elif IsInvitedExpert('@' + message.from_user.username, cursor, db):
        name = message.text
        bot.send_message(message.chat.id,
                         "Напишите, пожалуйста, в какиx областяx вы являетесь экспертом")
        SetState("@" + message.from_user.username, 101, cursor, db)
    else:
        name = message.text
        bot.send_message(message.chat.id,
                         "Отлично. Для контакта с вами нам может потребоваться номер вашего мобильного телефона. Введите его, пожалуйста")
        SetState("@" + message.from_user.username, 2, cursor, db)
    UpdateName('@' + message.from_user.username, name, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 101)
def user_entering_expertness(message):
    expertness = message.text
    UpdateExrtaInfo('@' + message.from_user.username, expertness, cursor, db)
    bot.send_message(message.chat.id,
                     "Отлично. Для контакта с вами нам может потребоваться номер вашего мобильного телефона. Введите его, пожалуйста")
    SetState("@" + message.from_user.username, 2, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 2)
def user_entering_phone(message):
    phone=message.text
    if re.fullmatch(r'\+7\d{10}', phone) or re.fullmatch(r'8\d{10}', phone):
        if IsAbit('@' + message.from_user.username, cursor, db):
            bot.send_message(message.chat.id, "Номер есть, тепeрь дай мне адрес электронной почты")
            SetState("@" + message.from_user.username, 3, cursor, db)
        else:
            bot.send_message(message.chat.id, "Также нам может потребоваться ваш адрес электронной почты. Введите и его.")
            SetState("@" + message.from_user.username, 3, cursor, db)
        UpdatePhone('@' + message.from_user.username, phone, cursor, db)
    else:
        bot.send_message(message.chat.id, 'Введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 3)
def user_entering_email(message):
    email = message.text
    if re.fullmatch(r'\w+@[a-z]+\.[a-z]{,4}', email):
        if IsAbit('@' + message.from_user.username, cursor, db):
            bot.send_message(message.chat.id, "Для полноценной работы в системе нужен Etherium-кошелек. Введи его адрес")
            SetState("@" + message.from_user.username, 5, cursor, db)
        else:
            bot.send_message(message.chat.id,
                             "Для полноценной работы в системе нужен Etherium-кошелек. Введите его адрес")
            SetState("@" + message.from_user.username, 5, cursor, db)
        UpdateEmail('@' + message.from_user.username, email, cursor, db)
    else:
        bot.send_message(message.chat.id, 'Введите адрес электронной почты в формате *@*.*')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 5)
def user_entering_wallet(message):
    if IsAbit('@' + message.from_user.username, cursor, db):
        wallet = message.text
        bot.send_message(message.chat.id, "Принял, теперь мне нужная твоя фотография, только давай без приколов")
        SetState("@" + message.from_user.username, 4, cursor, db)
    else:
        wallet = message.text
        bot.send_message(message.chat.id,
                         "Для упрощения нашего взаимодействия через систему загрузите, пожалуйста, свою фотографию.")
        SetState("@" + message.from_user.username, 4, cursor, db)
    UpdateWallet('@' + message.from_user.username, wallet, cursor, db)

@bot.message_handler(content_types=["photo"],
                     func=lambda message: GetState(message.from_user.username, cursor, db) == 4)
def user_entering_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    username = "@" + message.from_user.username
    if IsAbit(username, cursor, db):
        DeleteRang(username, 1, cursor, db)
        AddRang(username, 2, cursor, db)
        bot.send_message(message.chat.id, "Красавчик, спасибо. Отныне ты курсант антишколы Корпус!",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    elif IsInvitedInvestor(username, cursor, db):
        DeleteRang(username, 12, cursor, db)
        AddRang(username, 8, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    elif IsInvitedTutor(username, cursor, db):
        DeleteRang(username, 13, cursor, db)
        AddRang(username, 5, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    elif IsInvitedEducator(username, cursor, db):
        DeleteRang(username, 15, cursor, db)
        AddRang(username, 6, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    elif IsInvitedExpert(username, cursor, db):
        DeleteRang(username, 14, cursor, db)
        AddRang(username, 10, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    else:
        # UpdateProfile(username, user_info['name'], photo, user_info['phone'], user_info['email'], cursor, db)
        bot.send_message(message.chat.id, "Профиль обновлен",
                         reply_markup=get_keyboard('@' + message.from_user.username))
    UpdatePhoto(username, photo, cursor, db)
    BecomeBeginner(username, cursor, db)
    SetChatId('@' + message.from_user.username, message.chat.id, cursor, db)
    SetState("@" + message.from_user.username, 6, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 4)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 44)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(commands=["id"])
def get_id(message):
    if (message.chat.type == 'private'):
        SetChatId('@' + message.from_user.username, message.chat.id, cursor, db)
        bot.send_message(message.chat.id, 'Ok',
                         reply_markup=get_keyboard('@' + message.from_user.username))


budget_info = []


def send_budget_offer(message):
    if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
        if (IsThereActiveVoting(cursor)):
            bot.send_message(message.chat.id, 'В данный момент уже проходит голосование за утверждение бюджета',
                             reply_markup=get_keyboard('@' + message.from_user.username))
        else:
            bot.send_message(message.chat.id, 'Введите предполагаемую сумму бюджета')
            SetState('@' + message.from_user.username, 51, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 51)
def enter_budget_money(message):
    try:
        summa = int(message.text)
        config.budget = summa
        budget_info.append(summa)
        bot.send_message(message.chat.id, 'Вставьте ссылку на документ со сметой')
        SetState('@' + message.from_user.username, 52, cursor, db)
    except:
        bot.send_message(message.chat.id, 'Необходимо ввести число')


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 52)
def enter_budget_money(message):
    url = message.text
    budget_info.append(url)
    count = bot.get_chat_members_count(message.chat.id) - 1
    StartVoting(message.chat.id, '@' + message.from_user.username, count, budget_info[0], cursor, db)
    bot.send_message(message.chat.id,
                     'Утверждается бюджет на следующий месяц\nПодробности по ссылке: ' + url + '\nИтоговая сумма: ' +
                     budget_info[0],
                     reply_markup=get_keyboard('@' + message.from_user.username))
    members = GetListOfUsers(cursor)
    SetState('@' + message.from_user.username, 6, cursor, db)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="За", callback_data="voting_1"),
                 telebot.types.InlineKeyboardButton(text="Против", callback_data="voting_2"))
    for i in range(0, len(members)):
        if (members[i][2] != None and members[i][0] != '@' + message.from_user.username):
            bot.send_message(members[i][2],
                             'Началось голосование за утверждение бюджета. Подробности по ссылке: ' + url + '\nИтоговая сумма: ' +
                             budget_info[0] +
                             '\nВыразите ваше мнение', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('voting'))
def voting(call):
    BudgetVote(call.data[-1], cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, 'Спасибо за ваш голос! Текущий прогресс голосования:\n' + BudgetInfo(cursor),
                     reply_markup=get_keyboard('@' + call.from_user.username))


def finish_budget(message):
    if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
        if not (IsThereActiveVoting(cursor)):
            bot.send_message(message.chat.id, 'На данный момент активных голосований нет',
                             reply_markup=get_keyboard('@' + message.from_user.username))
        else:
            if (GetUserWhoStartedVoting(cursor) == '@' + message.from_user.username):
                bot.send_message(message.chat.id, 'Утверждение бюджета завершено. Результат:\n' + BudgetInfo(cursor),
                                 reply_markup=get_keyboard('@' + message.from_user.username))
                FinishVoting(cursor, db)
                emission(message)
            else:
                bot.send_message(message.chat.id, 'Голосование может завершить только тот, кто его начал',
                                 reply_markup=get_keyboard('@' + message.from_user.username))


def add_abit(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [5, 7, 9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы абитуриентов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
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
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            AddAbit(nick, cursor, db)
            bot.send_message(message.chat.id, "Абитуриент зачислен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


def add_investor(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы инвесторов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 811, cursor, db)


def add_tutor(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы тьюторов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 812, cursor, db)


def add_expert(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы экспертов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 813, cursor, db)


def add_educator(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы преподавателей, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 814, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 811)
def adding_investor(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все инвесторы успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteInvestor(nick, cursor, db)
            bot.send_message(message.chat.id, "Инвестор добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 812)
def adding_tutor(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все тьюторы успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteTutor(nick, cursor, db)
            bot.send_message(message.chat.id, "Тьютор добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 813)
def adding_expert(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все эксперты успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteExpert(nick, cursor, db)
            bot.send_message(message.chat.id, "Эксперт добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 814)
def adding_educator(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все преподаватели успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteEducator(nick, cursor, db)
            bot.send_message(message.chat.id, "Преподаватель добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


def marks(message):
    user = '@' + message.from_user.username
    if not (isRang(GetRangs('@' + message.from_user.username, cursor), [2, 3, 4])):
        bot.send_message(message.chat.id, 'Оценки можно просмотреть только у курсантов',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        return
    marks = GetMarks(user, cursor)
    if (len(marks) > 0):
        for i in range(0, len(marks)):
            if marks[i] == 2:
                marks[i] = 0.5
        for mark in marks:
            axis = int(mark[1])
            if axis == 1:
                bot.send_message(message.chat.id,
                                    'Оценки по оси отношений от ' + mark[2][1:] + ':\nЛичностное развитие: ' + mark[0][1] +
                                     '\nПонятность: ' + mark[0][2] + '\nЭнергия: ' + mark[0][3])
            elif axis == 2:
                bot.send_message(message.chat.id,
                                     'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение: ' + mark[0][1] +
                                     '\nЗавершенность: ' + mark[0][2] + '\nПодтверждение средой: ' + mark[0][3])
            elif axis == 3:
                bot.send_message(message.chat.id,
                                 'Оценки по оси власти от ' + mark[2][1:] + ':\nСамоуправление: ' +
                                 mark[0][1] +
                                 '\nСтратегия: ' + mark[0][2] + '\nУправляемость: ' + mark[0][3])
    else:
        bot.send_message(message.chat.id, 'Для данного пользователя пока нет оценок',
                         reply_markup=get_keyboard('@' + message.from_user.username))
    bot.send_message(message.chat.id, 'Главное меню',
                     reply_markup=get_keyboard('@' + message.from_user.username))


def look_marks(message):
    if message.chat.type == 'private' and isRang(GetRangs('@' + message.from_user.username, cursor), [5, 8, 9, 10]):
        users = GetListOfUsers(cursor)
        students = list()
        for user in users:
            if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
                students.append(user)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for student in students:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(student[0],cursor), callback_data='look_marks_of_' + student[0]))
        keyboard.add(telebot.types.InlineKeyboardButton(text='<Вернуться в главное меню>', callback_data='look_marks_of_*'))
        bot.send_message(message.chat.id, 'Выберите курсанта', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_marks_of'))
def looking_marks(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data[-1] == '*':
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard('@' + call.from_user.username))
    else:
        user = call.data[14:]
        if isRang(GetRangs(user, cursor), [2]):
            marks = GetMarks(user, cursor)
        else:
            marks = MarksOfSecondFlow(user, cursor)
        if (len(marks) > 0):
            for i in range(0, len(marks)):
                if marks[i] == 2:
                    marks[i] = 0.5
            for mark in marks:
                axis = int(mark[1])
                if axis == 1:
                    bot.send_message(call.message.chat.id,
                                     'Оценки по оси отношений от ' + mark[2][1:] + ':\nЛичностное развитие: ' + mark[0][
                                         1] + '\nПонятность: ' + mark[0][2] + '\nЭнергия: ' + mark[0][3])
                elif axis == 2:
                    bot.send_message(call.message.chat.id,
                                     'Оценки по оси дела от ' + mark[2][1:] + ':\nДвижение: ' + mark[0][1] +
                                     '\nЗавершенность: ' + mark[0][2] + '\nПодтверждение средой: ' + mark[0][3])
                elif axis == 3:
                    bot.send_message(call.message.chat.id,
                                     'Оценки по оси власти от ' + mark[2][1:] + ':\nСамоуправление: ' +
                                     mark[0][1] +
                                     '\nСтратегия: ' + mark[0][2] + '\nУправляемость: ' + mark[0][3])
        else:
            bot.send_message(call.message.chat.id, 'Для данного пользователя пока нет оценок',
                             reply_markup=get_keyboard('@' + call.from_user.username))
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard('@' + call.from_user.username))


def look_profiles(message):
    if message.chat.type == 'private' and isRang(GetRangs('@' + message.from_user.username, cursor), [5, 8, 9, 10]):
        students = GetListOfUsers(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for student in students:
            name = student[1]
            if name == None:
                name = student[0]
            keyboard.add(telebot.types.InlineKeyboardButton(text=name, callback_data='look_profile_of_' + student[0]))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text='<Вернуться в главное меню>', callback_data='look_profile_of_*'))
        bot.send_message(message.chat.id, 'Выберите пользователя', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_profile_of'))
def looking_profile(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data[-1] == '*':
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard('@' + call.from_user.username))
    else:
        profile = GetProfile(call.data[16:], cursor)
        if profile[0] != None:
            string = 'Пользователь: ' + profile[0]
            string += "\nФото: "
            bot.send_message(call.message.chat.id, string)
            if profile[3]!=None:
                bot.send_photo(call.message.chat.id, profile[3])
            else:
                bot.send_message(call.message.chat.id, 'Фото недоступно')
            try:
                string = "Телефон: " + str(profile[1])
                string = string + "\nЭлектронная почта: " + profile[2]
                string = string + "\nДата регистрации: " + profile[5]
                string = string + '\nАвторитет: ' + str(profile[4])
                if profile[6] != None:
                    string = string + '\nСумма оценок в текущем месяце: ' + str(profile[6])
                if profile[7] != None:
                    string = string + '\nДосье: ' + profile[8]
                wallet = GetWallet(call.data[16:], cursor)
                if wallet!= 'wallet':
                    string = string +'\nEtherium-кошелек:' + wallet
                try:
                    string = string + '\nТокены вклада: ' + str(
                        GetContributionTokens(call.data[16:], cursor))
                    string = string + '\nТокены инвестиций: ' + str(
                        GetInvestmentTokens(call.data[16:], cursor))
                except:
                    print("Fix it 2")
                string = string + '\nРоли в системе: '
                rangs = GetRangs(call.data[16:], cursor)
                for rang in rangs:
                    string = string + GetTitleOfRang(rang, cursor) + ', '
                string = string[:len(string) - 2]
                bot.send_message(call.message.chat.id, string,
                                 reply_markup=get_keyboard('@' + call.from_user.username))
            except:
                bot.send_message(call.message.chat.id, "Анкета заполнена не полностью",
                                 reply_markup=get_keyboard('@' + call.from_user.username))
        else:
            bot.send_message(call.message.chat.id, "Ой, анкета еще не заполнена",
                             reply_markup=get_keyboard('@' + call.from_user.username))

def set_rang(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0],cursor), callback_data='csr%' + user[0]))
    keyboard.add(telebot.types.InlineKeyboardButton(text='<Назад>', callback_data='csr%back'))
    bot.send_message(message.chat.id, 'Чей ранг вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('csr'))
def setting_rang1(call):
    if call.data.split('%')[1] == 'back':
        SetState('@'+call.from_user.username, 6, cursor, db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Главное меню",
                         reply_markup=get_keyboard('@' + call.from_user.username))
    else:
        nick = call.data.split('%')[1]
        rangs = GetRangs(nick, cursor)
        str_rang = ''
        for rang in rangs:
            str_rang = str_rang + GetTitleOfRang(rang, cursor) + ', '
        str_rang = str_rang[:len(str_rang) - 2]
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Первый курс', callback_data='set_rang_2#' + nick),
                     telebot.types.InlineKeyboardButton(text='Второй курс', callback_data='set_rang_3#' + nick),
                     telebot.types.InlineKeyboardButton(text='Третий курс', callback_data='set_rang_4#' + nick))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Тьютор', callback_data='set_rang_5#' + nick),
                     telebot.types.InlineKeyboardButton(text='Преподаватель', callback_data='set_rang_6#' + nick),
                     telebot.types.InlineKeyboardButton(text='Завуч', callback_data='set_rang_11#' + nick))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Сталкер', callback_data='set_rang_7#' + nick),
                     telebot.types.InlineKeyboardButton(text='Эксперт', callback_data='set_rang_10#' + nick))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Инвестор', callback_data='set_rang_8#' + nick),
                     telebot.types.InlineKeyboardButton(text='Администратор', callback_data='set_rang_9#' + nick))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Выберите роль для пользователя ' + GetName(nick,cursor) + ' (текущие роли: ' + str_rang + ')',
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('set_rang'))
def setting_rang2(call):
    text = call.data[9:]
    words = text.split('#')
    rang = int(words[0])
    nick = words[1]
    AddRang(nick, rang, cursor, db)
    SetState(nick, 6, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Успешно",
                     reply_markup=get_keyboard('@' + call.from_user.username))


def delete_rang(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0],cursor), callback_data='cdr%' + user[0]))
    keyboard.add(telebot.types.InlineKeyboardButton(text='<Назад>', callback_data='cdr%back'))
    bot.send_message(message.chat.id, 'Чей ранг вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('cdr'))
def deleting_rang1(call):
    nick = call.data.split('%')[1]
    if nick == 'back':
        SetState('@' + call.from_user.username, 6, cursor, db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Главное меню",
                         reply_markup=get_keyboard('@' + call.from_user.username))
    else:
        rangs = GetRangs(nick, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for rang in rangs:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetTitleOfRang(rang, cursor),
                                                            callback_data='del_rang%' + str(rang) + '%' + nick))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Выберите роль, которую вы хотите убрать у пользователя ' + GetName(nick, cursor),
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('del_rang'))
def deleting_rang2(call):
    words = call.data.split('%')
    rang = words[1]
    nick = words[2]
    DeleteRang(nick, int(rang), cursor, db)
    SetState(nick, 6, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Успешно",
                     reply_markup=get_keyboard('@' + call.from_user.username))


def add_dosier(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
            name = user[1]
            if name == None:
                name = user[0]
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=name, callback_data='add_dosier%' + user[0]))
    bot.send_message(message.chat.id, 'Кому вы хотите добавить или изменить досье?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('add_dosier'))
def setting_dosier1(call):
    nick = call.data.split('%')[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,
                     'Вставьте ссылку на документ с досье курсанта или отправьте его в виде сообщения')
    SetState('@' + call.from_user.username, 61, cursor, db)
    config.current_user_for_dossier = nick


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 61)
def setting_dosier2(message):
    dossier = message.text
    SetDossier(dossier, config.current_user_for_dossier, cursor, db)
    SetState('@' + message.from_user.username, 6, cursor, db)
    bot.send_message(message.chat.id, "Успешно",
                     reply_markup=get_keyboard('@' + message.from_user.username))


def look_dosier(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
            name = user[1]
            if name == None:
                name = user[0]
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=name, callback_data='look_dosier%' + user[0]))
    bot.send_message(message.chat.id, 'Чьё досье вы хотите посмотреть?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_dosier'))
def looking_dosier(call):
    nick = call.data.split('%')[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    dossier = GetDossier(nick, cursor)
    if dossier == -1:
        bot.send_message(call.message.chat.id, 'Досье для данного пользователя еще не добавлено',
                         reply_markup=get_keyboard('@' + call.from_user.username))
    else:
        bot.send_message(call.message.chat.id, 'Досье пользователя ' + nick + ':\n\n' + dossier,
                         reply_markup=get_keyboard('@' + call.from_user.username))


def emission(message):
    all_marks = GetAllMarks(cursor)
    marks_sum = 0
    for mark in all_marks:
        if mark[0] != None and isRang(GetRangs(mark[1], cursor), [2, 3, 4]):
            marks_sum += mark[0]
    budget = GetSumOfBudget(cursor)
    summa_for_students = budget / 7 * 3
    coeff = summa_for_students / marks_sum
    SetCoeff(coeff, cursor, db)
    for i in all_marks:
        if i[0] != None:
            bot.send_message(message.chat.id, i[1] + ' получит ' + str(coeff * i[0]))


def give_tokens(message):
    tokens = GetContributionTokens('@'+message.from_user.username,cursor)
    if tokens == 0.0 :
        bot.send_message(message.chat.id, 'У вас на счету нет токенов вклада', reply_markup=get_keyboard('@'+message.from_user.username))
    else:
        bot.send_message(message.chat.id, 'У вас на счету <b>'+str(tokens)+'</b> токенов вклада. Сколько из них вы хотите переслать?',parse_mode='HTML')
        SetState('@'+message.from_user.username,71,cursor,db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 71)
def give_tokens_2(message):
    try:
        tokens = float(message.text)
        if tokens > float(GetContributionTokens('@'+message.from_user.username,cursor)):
            bot.send_message(message.chat.id,'У вас на счету недостаточно токенов вклада. Введите меньшую сумму')
        else:
            users = GetListOfUsers(cursor)
            keyboard = telebot.types.InlineKeyboardMarkup()
            for user in users:
                try:
                    keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0], cursor)+'('+str(GetContributionTokens(user[0],cursor))+' токенов на счету)',
                                                                callback_data='give_tokens%' + user[0]+'%'+str(tokens)))
                except:
                    continue
            bot.send_message(message.chat.id, "Кому вы хотите передать токены вклада?",reply_markup=keyboard)
            SetState('@' + message.from_user.username, 6, cursor, db)
    except:
        bot.send_message(message.chat.id, 'Необходимо ввести число')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('give_tokens'))
def give_tokens3(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    nick = call.data.split('%')[1]
    tokens = float(call.data.split('%')[2])
    AddContributionTokens(nick, tokens, cursor, db)
    ReduceContributionTokens('@'+call.from_user.username, tokens, cursor, db)
    bot.send_message(GetChatId(nick,cursor),'Пользователь @'+call.from_user.username+' перевел вам на счет '+str(tokens)+' токенов вклада')
    bot.send_message(call.message.chat.id, "Успешно",
                     reply_markup=get_keyboard('@' + call.from_user.username))

def ask_tokens(message):
    SetState('@' + message.from_user.username, 72, cursor, db)
    tokens = GetContributionTokens('@' + message.from_user.username, cursor)
    bot.send_message(message.chat.id, 'Сколько токенов вы хотите попросить? (сейчас на счету ' + str(
            tokens) + ' токенов вклада)')

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 72)
def ask_tokens2(message):
    try:
        tokens = float(message.text)
        users = GetListOfUsers(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        flag = False
        for user in users:
            try:
                user_tokens = GetContributionTokens(user[0], cursor)
                if user_tokens>=tokens:
                    flag = True
                    keyboard.add(telebot.types.InlineKeyboardButton(
                        text=GetName(user[0], cursor) + '(' + str(user_tokens) + ' токенов на счету)',
                        callback_data='ask_tokens%' + user[0] + '%' + str(tokens)))
            except:
                continue
        if flag:
            bot.send_message(message.chat.id, "У кого вы хотите попросить токены?", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Ни у кого нет достаточного количества токенов для данной сделки",
                             reply_markup=get_keyboard('@'+message.from_user.username))
        SetState('@' + message.from_user.username, 6, cursor, db)
    except:
        bot.send_message(message.chat.id, 'Необходимо ввести число')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('ask_tokens'))
def ask_tokens3(call):
    nick = call.data.split('%')[1]
    tokens = float(call.data.split('%')[2])
    keyboard = telebot.types.InlineKeyboardMarkup()
    id = OrganizeExchange('@'+call.from_user.username,nick,tokens,cursor,db)
    keyboard.row(telebot.types.InlineKeyboardButton(text='Да',callback_data='exchange_'+str(id)+'_yes'),
                 telebot.types.InlineKeyboardButton(text='Нет', callback_data='exchange_' + str(id) + '_no'))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(GetChatId(nick,cursor),"Пользователь "+GetName('@'+call.from_user.username,cursor)+' просит у вас '+str(tokens)+
                     ' токенов вклада (у вас на счету '+str(GetContributionTokens(nick,cursor))+'). Вы согласны на сделку?',
                     reply_markup=keyboard)
    bot.send_message(call.message.chat.id,'Предложение пользователю '+GetName(nick,cursor)+'. Дождитесь, пока он ответит на него.',
                     reply_markup=get_keyboard('@'+call.from_user.username))

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('exchange'))
def exchange(call):
    id = call.data.split('_')[1]
    desicion = call.data.split('_')[2]
    if desicion=='yes':
        asker = AcceptExchange('@'+call.from_user.username,id,cursor,db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,'Обмен токенами завершен. Теперь у вас на счету '+
                         str(GetContributionTokens('@'+call.from_user.username,cursor))+' токенов вклада')
        bot.send_message(GetChatId(asker,cursor),'Пользователь '+GetName('@'+call.from_user.username,cursor)+
                         ' согласился поделиться токенами. Теперь у вас на счету '+str(GetContributionTokens(asker,cursor))+' токенов вклада')
    else:
        asker=DenyExchange(id,cursor,db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Предложение отклонено')
        bot.send_message(GetChatId(asker, cursor), 'Пользователь ' + GetName('@' + call.from_user.username, cursor) +' отклонил ваш запрос')


def change_investment_tokens(message):
    bot.send_message(message.chat.id,'Сколько токенов инвестиции вы хотите поменять?(на счету '+
                     str(GetInvestmentTokens('@'+message.from_user.username,cursor))+')')
    SetState('@'+message.from_user.username,73,cursor,db)

@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 73)
def change_tokens2(message):
    try:
        tokens = float(message.text)
        if tokens>float(GetInvestmentTokens('@'+message.from_user.username,cursor)):
            bot.send_message(message.chat.id, 'У вас на счету недостаточно токенов вклада. Введите меньшую сумму')
        else:
            AddContributionTokens('@'+message.from_user.username,tokens,cursor,db)
            ReduceInvestmentTokens('@'+message.from_user.username,tokens,cursor,db)
            SetState('@' + message.from_user.username, 6, cursor,db)
            bot.send_message(message.chat.id, "Успешно",
                             reply_markup=get_keyboard('@' + message.from_user.username))
    except:
        bot.send_message(message.chat.id, 'Необходимо ввести число')

@bot.message_handler(content_types=["text"])
def text(message):
    f = open('errorcherry.log', 'a')
    f.write('access from webhook')
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
            if GetAuthority('@' + message.from_user.username, cursor) > 0 or isRang(
                    GetRangs('@' + message.from_user.username, cursor), [2, 3, 5, 6, 7, 10]):
                keyboard.add(emojize(':crown: Оценить нематериальный вклад участников'))
            if isRang(GetRangs('@' + message.from_user.username, cursor), [2, 3, 4]):
                keyboard.add(emojize(':eyes: Посмотреть свои оценки'))
            if isRang(GetRangs('@' + message.from_user.username, cursor), [5, 8, 9, 10]):
                keyboard.add(emojize(':newspaper: Оценки пользователей'))
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Оценки"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == '👑 Оценить нематериальный вклад участников':
            start_voting(message)
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
            if IsThereActiveVoting(cursor):
                keyboard.add('Закончить утверждение бюджета')
            else:
                keyboard.add(emojize(':loudspeaker: Начать голосование за утверждение бюджета'))
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
            if not (AreThereCourseVotings(cursor)):
                keyboard.add("Разрешить голосование курсантам")
            else:
                keyboard.add('Закончить голосование курсантов')
            keyboard.row('Добавить досье пользователю', 'Посмотреть досье пользователя')
            keyboard.add('Назад')
            bot.send_message(message.chat.id, 'Вкладка <b>"Тьютор"</b>', reply_markup=keyboard, parse_mode='HTML')
        elif mess == 'Добавить досье пользователю':
            add_dosier(message)
        elif mess == 'Посмотреть досье пользователя':
            look_dosier(message)
        elif mess == 'Разрешить голосование курсантам':
            StartCourseVoting('@' + message.from_user.username, cursor, db)
            bot.send_message(message.chat.id,
                             'Теперь курсанты могут оценивать друг друга, пока вы не закончите голосование',
                             reply_markup=get_keyboard('@' + message.from_user.username))
        elif mess == 'Закончить голосование курсантов':
            if '@' + message.from_user.username == WhoStartedCourseVoting(cursor):
                FinishCourseVoting(cursor, db)
                bot.send_message(message.chat.id,
                                 'Голосование курсантов окончено',
                                 reply_markup=get_keyboard('@' + message.from_user.username))
            else:
                bot.send_message(message.chat.id,
                                 'Голосование может начать только тот, кто его начал',
                                 reply_markup=get_keyboard('@' + message.from_user.username))
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
    f.close()

import logging

logging.basicConfig(filename="log.log", level=logging.INFO)
try:
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%y %H:%M")
    logging.info('['+now_date+'] Bot started')
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
    d.subscribe()
except:
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%y %H:%M")
    logging.debug('[' + now_date + '] Bot dropped')

now_date = datetime.datetime.today()
now_date = now_date.strftime("%d/%m/%y %H:%M")
logging.info('['+now_date+'] Bot finished')



# bot.polling(none_stop=True)

