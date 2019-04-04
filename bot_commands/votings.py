# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_voting import *
from db_commands.db_projects import *
from db_commands.db_marks import GetMarksForDate
import telebot
import re
from config import bot, db, cursor, get_keyboard
import config


def contribution(message):
    projects = GetLeadProjects('@'+message.from_user.username,cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(projects) > 0:
        for project in projects:
            keyboard.add(telebot.types.InlineKeyboardButton(text=project[0],callback_data='proj_vot%'+str(project[1])))
        bot.send_message(message.chat.id, 'Выберите проект для проведения оценки', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Нет доступных проектов для оценки',
                         reply_markup=get_keyboard('@'+message.from_user.username))


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('proj_vot'))
def choose_project(call):
    project_id = call.data.split('%')[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    voting_menu('@'+call.from_user.username,project_id)


def voting_menu(user,project_id):
    last_voting = GetLastVotingsByProject(project_id, cursor)
    next_voting = GetNextVotingDateByProject(project_id, cursor)
    OrganizeNewVoting(project_id, cursor, db)
    voting = GetCurrentPreparingVoting(project_id, cursor)
    info = ''
    if last_voting is None or last_voting[1] is None:
        info += 'Оценок по данному проекту пока не проводилось\n'
    else:
        info += 'Предыдущая оценка по данному проекту проводилась ' + last_voting[1] + '\n'
    info += 'Информация о предстоящей оценке:\n\n'
    if next_voting is None or next_voting[1] is None:
        info += 'Дата оценки пока не назначена\n'
    else:
        info += 'Оценка запланирована на <b>' + next_voting[1] + '</b>\n'
    communication_experts = GetExpertsFromVoting(voting,1,cursor)
    business_experts = GetExpertsFromVoting(voting,2,cursor)
    authority_experts = GetExpertsFromVoting(voting,3,cursor)

    if len(communication_experts) == 0:
        info += 'Эксперты по оси отношений еще не выбраны\n'
    else:
        info += 'Эксперты по оси отношений: '
        for expert in communication_experts:
            info += '<b>' + GetName(expert[0], cursor) + '</b>'
            if expert[1] == 'Not confirmed':
                info += '(приглашение отправлено)'
            info += ', '
        info = info[:len(info) - 2]
        info += '\n'

    if len(business_experts) == 0:
        info += 'Эксперты по оси дела еще не выбраны\n'
    else:
        info += 'Эксперты по оси дела: '
        for expert in business_experts:
            info += '<b>' + GetName(expert[0], cursor) + '</b>'
            if expert[1] == 'Not confirmed':
                info += '(приглашение отправлено)'
            info += ', '
        info = info[:len(info) - 2]
        info += '\n'

    if len(authority_experts) == 0:
        info += 'Эксперты по оси власти еще не выбраны\n'
    else:
        info += 'Эксперты по оси власти: '
        for expert in authority_experts:
            info += '<b>' + GetName(expert[0], cursor) + '</b>'
            if expert[1] == 'Not confirmed':
                info += '(приглашение отправлено)'
            info += ', '
        info = info[:len(info) - 2]
        info += '\n'

    bot.send_message(GetChatId(user, cursor), info, parse_mode='HTML')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назначить дату следующей оценки',
                                                    callback_data='date_vot%' + str(project_id) + '%' + str(voting)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Пригласить экспертов для оценки',
                                                    callback_data='exp_vot%' + str(project_id) + '%' + str(voting)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Напомнить экспертам о скором начале голосования',
                                                    callback_data='remind_vot%' + str(project_id) + '%' + str(voting)))
    if IsVotingPreparing(project_id,voting,cursor):
        keyboard.add(telebot.types.InlineKeyboardButton(text='Начать оценку',
                                                    callback_data='start_vot%' + str(project_id) + '%' + str(voting)))
    if IsVotingStarted(project_id, voting, cursor):
        keyboard.add(telebot.types.InlineKeyboardButton(text='Завершить оценку',
                                                        callback_data='end_vot%' + str(project_id) + '%' + str(voting)))
    bot.send_message(GetChatId(user,cursor), 'Выберите дальнейшее действие', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True and call.data.startswith('remind_vot'))
def remind(call):
    project_id = call.data.split('%')[1]
    voting_id = call.data.split('%')[2]
    communication_experts = GetExpertsFromVoting(voting_id, 1, cursor)
    business_experts = GetExpertsFromVoting(voting_id, 2, cursor)
    authority_experts = GetExpertsFromVoting(voting_id, 3, cursor)
    info = 'Внимание! Скоро начнется оценка нематериального вклада курсантов в проекте "' + \
           GetProjectTitle(project_id, cursor) + '". Будьте готовы к оценке по оси '
    for expert in communication_experts:
        bot.send_message(GetChatId(expert[0], cursor), info + 'отношений')
    for expert in business_experts:
        bot.send_message(GetChatId(expert[0], cursor), info + 'дела')
    for expert in authority_experts:
        bot.send_message(GetChatId(expert[0], cursor), info + 'власти')
    bot.send_message(call.message.chat.id, 'Напоминания экспертам разосланы')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('date_vot'))
def choose_date(call):
    id = call.data.split('%')[1]
    voting = call.data.split('%')[2]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,'Введите дату и время, когда вы планируете начать оценивание вклада по проекту "'+
                     GetProjectTitle(id,cursor)+'" в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')
    SetState('@'+call.from_user.username,91,cursor,db)
    SetEditingVoting('@'+call.from_user.username,voting,cursor,db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 91)
def set_date(message):
    time = message.text
    if re.fullmatch(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', time):
        bot.send_message(message.chat.id,'Спасибо, время зафиксировано')
        SetState('@' + message.from_user.username, 6, cursor, db)
        SetDate(GetEditingVoting('@'+message.from_user.username,cursor),time,cursor,db)
        voting_menu('@'+message.from_user.username,
                    GetProjectIdByPreparingVotingId(GetEditingVoting('@'+message.from_user.username,cursor),cursor))
    else:
        bot.send_message(message.chat.id, 'Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('exp_vot'))
def axis_menu(call):
    project_id = call.data.split('%')[1]
    voting = call.data.split('%')[2]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    choose_axis(project_id,voting,'@'+call.from_user.username)


def choose_axis(project_id, voting_id, user):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось отношений',
                                                    callback_data='axis_vot%1%' + str(project_id) + '%' + str(voting_id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось дела',
                                                    callback_data='axis_vot%2%' + str(project_id) + '%' + str(voting_id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Ось власти',
                                                    callback_data='axis_vot%3%' + str(project_id) + '%' + str(voting_id)))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Назад',
                                                    callback_data='axis_vot%4%' + str(project_id) + '%' + str(voting_id)))
    bot.send_message(GetChatId(user, cursor), 'Выберите ось', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('axis_vot'))
def set_experts(call):
    items = call.data.split('%')
    axis = items[1]
    project_id = items[2]
    voting_id = items[3]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if axis == '1':
        experts = GetExpertsFromProject(project_id, cursor)
        all_members = GetListOfUsers(cursor)
        for member in all_members:
            if isRang(GetRangs(member[0], cursor), [5, 11]):
                experts.append(member)
        if len(experts) > 0:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for expert in experts:
                keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(expert[0],cursor), callback_data='expert%1%'+expert[0]+'%'+str(project_id)+'%'+str(voting_id)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Завершить выбор', callback_data='expert%1%0'+'%'+str(project_id)+'%'+str(voting_id)))
            bot.send_message(call.message.chat.id, 'Выберите экспертов из списка', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,'В данном момент пока нет экспертов, которые могут оценивать ось отношений')
            choose_axis(project_id,voting_id,'@'+call.from_user.username)
    elif axis == '2':
        experts = GetExpertsFromProject(project_id,cursor)
        if len(experts) > 0:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for expert in experts:
                keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(expert[0],cursor), callback_data='expert%2%'+expert[0]+'%'+str(project_id)+'%'+str(voting_id)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Завершить выбор', callback_data='expert%2%0'+'%'+str(project_id)+'%'+str(voting_id)))
            bot.send_message(call.message.chat.id, 'Выберите экспертов из списка', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,'В данном проекте пока нет экспертов, которые могут оценивать ось дела')
            choose_axis(project_id,voting_id,'@'+call.from_user.username)
    elif axis == '3':
        all_members = GetListOfUsers(cursor)
        experts = list()
        for member in all_members:
            if isRang(GetRangs(member[0],cursor),[5,10,11]):
                experts.append(member[0])
        if len(experts) > 0:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for expert in experts:
                keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(expert, cursor),
                                                                    callback_data='expert%3%' + expert + '%' + str(project_id) + '%' + str(voting_id)))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Завершить выбор',
                                                                callback_data='expert%3%0' + '%' + str(project_id) + '%' + str(voting_id)))
            bot.send_message(call.message.chat.id, 'Выберите экспертов из списка', reply_markup=keyboard)
        else:
            bot.send_message(call.message.message.id,'В данный момент нет экспертов, которые могут оценивать ось власти')
            choose_axis(project_id,voting_id,'@'+call.from_user.username)
    else:
        voting_menu('@'+call.from_user.username,project_id)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('expert'))
def send_invite(call):
    axis = call.data.split('%')[1]
    nick = call.data.split('%')[2]
    project_id = call.data.split('%')[3]
    voting_id = call.data.split('%')[4]
    if nick == '0':
        choose_axis(project_id, voting_id, '@'+call.from_user.username)
    else:
        experts = GetExpertsFromVoting(voting_id, axis, cursor)
        flag = True
        for expert in experts:
            if expert[0]==nick:
                flag = False
        if flag:
            bot.send_message(call.message.chat.id, 'Приглашение отправлено')
            AddExpertToVoting(nick, voting_id, axis, cursor, db)
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(telebot.types.InlineKeyboardButton(text='Принять', callback_data='exp_decide%1%'+axis+'%'+project_id+'%'+voting_id),
                         telebot.types.InlineKeyboardButton(text='Отклонить',
                                                            callback_data='exp_decide%2%' + axis + '%' + project_id + '%' + voting_id))
            info = GetName('@'+call.from_user.username,cursor) + ' пригласил вас  для оценки вклада курсантов по оси '
            if axis == '1':
                info += 'отношений '
            elif axis == '2':
                info += 'дела '
            else:
                info += 'власти '
            info += 'в проекте "' + GetProjectTitle(project_id, cursor) + '".'
            try:
                info += ' Ожидаемое время оценки: '+GetNextVotingDateByProject(project_id, cursor)[1]
            except:
                info += 'Время оценки пока не назначено'
            bot.send_message(GetChatId(nick,cursor), info, reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, 'Вы уже отправляли приглашение этому эксперту')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('exp_decide'))
def decide_expert(call):
    desicion = call.data.split('%')[1]
    axis = call.data.split('%')[2]
    project_id = call.data.split('%')[3]
    voting_id = call.data.split('%')[4]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    mess = 'Эксперт '+GetName('@'+call.from_user.username,cursor)+', приглашенный оценивать вклад курсантов по оси '
    if axis == '1':
        mess += 'отношений '
    elif axis == '2':
        mess += 'дела '
    else:
        mess += 'власти '
    mess += 'в проекте "'+GetProjectTitle(project_id,cursor) + '", '
    if desicion == '1':
        ExpertDecisedInVoting('@' + call.from_user.username, voting_id, axis, 'Accepted', cursor, db)
        mess += ' принял'
    else:
        ExpertDecisedInVoting('@' + call.from_user.username, voting_id, axis, 'Denied', cursor, db)
        mess += ' отклонил'
    mess += ' приглашение'
    bot.send_message(call.message.chat.id, 'Спасибо, ваше мнение учтено')
    bot.send_message(GetChatId(GetTeamleadOfProject(project_id,cursor)[0],cursor),mess)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('start_vot'))
def start_voting(call):
    project_id = call.data.split('%')[1]
    voting_id = call.data.split('%')[2]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if IsVotingReadyForStart(voting_id, cursor):
        bot.send_message(call.message.chat.id,
                         'Голосование началось, всем участвующим экспертам разосланы формы для голосования')
        StartVoting(voting_id, cursor, db)
        communication_experts = GetExpertsFromVoting(voting_id, 1, cursor)
        business_experts = GetExpertsFromVoting(voting_id, 2, cursor)
        authority_experts = GetExpertsFromVoting(voting_id, 3, cursor)
        project_members = GetMembersOfProject(project_id, cursor)
        for expert in communication_experts:
            for member in project_members:
                PutEmptyMark(voting_id,expert[0],member[0],1,cursor,db)
            cadet = GetNonvotedCadetsForExpert(voting_id,expert[0],1,cursor)[0][0]
            bot.send_message(GetChatId(expert[0],cursor),
                                    'Оценка нематериального вклада\nПроект <b>"'+GetProjectTitle(project_id,cursor)+
                                    '"</b>\nОсь отношений\nКурсант: <b>' + GetName(cadet,cursor) +
                                    '</b>\nЛичностное развитие: 0\nПонятность: 0\nЭнергия: 0',
                                    reply_markup=config.ChooseKeyboardForRelations(voting_id, cadet), parse_mode='HTML')
        for expert in business_experts:
            for member in project_members:
                PutEmptyMark(voting_id,expert[0],member[0],2,cursor,db)
            cadet = GetNonvotedCadetsForExpert(voting_id,expert[0],2,cursor)[0][0]
            bot.send_message(GetChatId(expert[0], cursor),
                             'Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                             '"</b>\nОсь дела\nКурсант: <b>' + GetName(cadet, cursor) +
                             '</b>\nДвижение: 0\nЗавершенность: 0\nПодтверждение средой: 0',
                             reply_markup=config.ChooseKeyboardForBusiness(voting_id, cadet), parse_mode='HTML')
        for expert in authority_experts:
            for member in project_members:
                PutEmptyMark(voting_id, expert[0], member[0], 3, cursor, db)
            cadet = GetNonvotedCadetsForExpert(voting_id, expert[0], 3, cursor)[0][0]
            bot.send_message(GetChatId(expert[0],cursor),
                             'Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                             '"</b>\nОсь власти\nКурсант: <b>' + GetName(cadet, cursor) +
                             '</b>\nСамоуправление: 0\nСтратегия: 0\nУправляемость: 0',
                             reply_markup=config.ChooseKeyboardForAuthority(voting_id, cadet), parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id,
                         'Вы пока не можете начать голосование. Ни один эксперт пока не подтвердил участие или не выставлена дата')
        voting_menu('@' + call.from_user.username,project_id)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('relations'))
def relations_voting(call):
    criterion = call.data.split('%')[1]
    voting_id = call.data.split('%')[2]
    cadet = call.data.split('%')[3]
    project_id = GetProjectIdByPreparingVotingId(voting_id, cursor)
    expert = '@' + call.from_user.username
    if criterion != '4':
        mark = GetMarkInVoting(voting_id,expert,cadet,1,criterion,cursor)
        if mark is None or mark == 0 or mark == '0':
            PutMark(voting_id,expert,cadet,1,criterion,1,cursor,db)
        else:
            PutMark(voting_id, expert, cadet, 1, criterion, 0, cursor, db)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             text='Оценка нематериального вклада\n<b>Проект "' + GetProjectTitle(project_id, cursor) +
                                '"</b>\nОсь отношений\nКурсант: <b>' + GetName(cadet, cursor) +
                                '</b>\nЛичностное развитие: '+str(GetMarkInVoting(voting_id,expert,cadet,1,1,cursor))+
                                '\nПонятность: '+str(GetMarkInVoting(voting_id,expert,cadet,1,2,cursor))+
                                '\nЭнергия: '+str(GetMarkInVoting(voting_id,expert,cadet,1,3,cursor)),
                             reply_markup=config.ChooseKeyboardForRelations(voting_id, cadet), parse_mode='HTML')
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # commenting(expert,cadet,voting_id,1)
        AcceptMark(voting_id, expert, cadet, 1, cursor, db)
        cadets = GetNonvotedCadetsForExpert(voting_id, '@'+call.from_user.username, 1, cursor)
        if cadets is None or len(cadets) == 0:
            bot.send_message(call.message.chat.id,
                             'Спасибо за ваши оценки, ваше голосование по оси отношений завершено окончено')
            if IsVotingFinished(voting_id, 1, cursor):
                CompileMarksByAxis(voting_id, 1, cursor, db)
                cursor.execute('SELECT voting_date FROM votings WHERE id=' + str(voting_id))
                time = cursor.fetchone()[0]
                marks = GetMarksForDate(time, 1, cursor)
                cur_cadet = marks[0][0]
                result = '<b>Результаты оценки по оси отношений в проекте "' + GetProjectTitle(project_id, cursor) \
                         + '"</b>\nКурсант: <b>' + GetName(cur_cadet, cursor) + '</b>\n'
                FinishVoting(voting_id, cursor, db)
                for mark in marks:
                    if mark[0] == cur_cadet:
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Личностное развитие'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Понятность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Энергия'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                    else:
                        cur_cadet = mark[0]
                        result += '\nКурсант: <b>' + GetName(mark[0], cursor) + '</b>\n'
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Личностное развитие'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Понятность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Энергия'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                members = GetMembersOfProject(project_id, cursor)
                experts = GetExpertsFromVoting(voting_id, 1, cursor)
                for member in members:
                    bot.send_message(GetChatId(member[0], cursor), result, parse_mode='HTML')
                for expert in experts:
                    bot.send_message(GetChatId(expert[0], cursor), result, parse_mode='HTML')
        else:
            cadet = cadets[0][0]
            bot.send_message(GetChatId(expert, cursor),
                             'Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                             '"</b>\nОсь отношений\nКурсант: <b>' + GetName(cadet, cursor) +
                             '</b>\nЛичностное развитие: 0\nПонятность: 0\nЭнергия: 0',
                             reply_markup=config.ChooseKeyboardForRelations(voting_id, cadet), parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('business'))
def business_voting(call):
    criterion = call.data.split('%')[1]
    voting_id = call.data.split('%')[2]
    cadet = call.data.split('%')[3]
    project_id = GetProjectIdByPreparingVotingId(voting_id, cursor)
    expert = '@' + call.from_user.username
    if criterion != '4':
        mark = GetMarkInVoting(voting_id,expert,cadet,2,criterion,cursor)
        if mark is None or mark == 0 or mark == '0':
            PutMark(voting_id,expert,cadet,2,criterion,1,cursor,db)
        else:
            PutMark(voting_id, expert, cadet, 2, criterion, 0, cursor, db)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             text='Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                                '"</b>\nОсь дела\nКурсант: <b>' + GetName(cadet, cursor) +
                                '</b>\nДвижение: '+str(GetMarkInVoting(voting_id,expert,cadet,2,1,cursor))+
                                '\nЗавершенность: '+str(GetMarkInVoting(voting_id,expert,cadet,2,2,cursor))+
                                '\nПодтверждение средой: '+str(GetMarkInVoting(voting_id,expert,cadet,2,3,cursor)),
                             reply_markup=config.ChooseKeyboardForBusiness(voting_id, cadet), parse_mode='HTML')
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # commenting(expert,cadet,voting_id,2)
        AcceptMark(voting_id, expert, cadet, 2, cursor, db)
        cadets = GetNonvotedCadetsForExpert(voting_id, '@'+call.from_user.username, 2, cursor)
        if cadets is None or len(cadets) == 0:
            bot.send_message(call.message.chat.id, 'Спасибо за ваши оценки, ваше голосование по оси дела окончено')
            if IsVotingFinished(voting_id, 2, cursor):
                CompileMarksByAxis(voting_id, 2, cursor, db)
                cursor.execute('SELECT voting_date FROM votings WHERE id=' + str(voting_id))
                time = cursor.fetchone()[0]
                marks = GetMarksForDate(time, 2, cursor)
                cur_cadet = marks[0][0]
                result = '<b>Результаты оценки по оси дела в проекте "' + GetProjectTitle(project_id, cursor) \
                         + '"</b>\nКурсант: <b>' + GetName(cur_cadet, cursor) + '</b>\n'
                FinishVoting(voting_id, cursor, db)
                for mark in marks:
                    if mark[0] == cur_cadet:
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Движение'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Завершенность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Подтверждение средой'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                    else:
                        cur_cadet = mark[0]
                        result += '\nКурсант: <b>' + GetName(mark[0], cursor) + '</b>\n'
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Движение'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Завершенность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Подтверждение средой'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                members = GetMembersOfProject(project_id, cursor)
                experts = GetExpertsFromVoting(voting_id, 2, cursor)
                for member in members:
                    bot.send_message(GetChatId(member[0], cursor), result, parse_mode='HTML')
                for expert in experts:
                    bot.send_message(GetChatId(expert[0], cursor), result, parse_mode='HTML')
        else:
            cadet = cadets[0][0]
            bot.send_message(GetChatId(expert, cursor),
                             'Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                             '"</b>\nОсь дела\nКурсант: <b>' + GetName(cadet, cursor) +
                             '</b>\nДвижение: 0\nЗавершенность: 0\nПодтверждение средой: 0',
                             reply_markup=config.ChooseKeyboardForBusiness(voting_id, cadet), parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('authority'))
def authority_voting(call):
    criterion = call.data.split('%')[1]
    voting_id = call.data.split('%')[2]
    cadet = call.data.split('%')[3]
    project_id = GetProjectIdByPreparingVotingId(voting_id, cursor)
    expert = '@' + call.from_user.username
    if criterion != '4':
        mark = GetMarkInVoting(voting_id,expert,cadet,3,criterion,cursor)
        if mark is None or mark == 0 or mark == '0':
            PutMark(voting_id,expert,cadet,3,criterion,1,cursor,db)
        else:
            PutMark(voting_id, expert, cadet, 3, criterion, 0, cursor, db)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                                '"</b>\nОсь власти\nКурсант: <b>' + GetName(cadet, cursor) +
                                '</b>\nСамоуправление: '+str(GetMarkInVoting(voting_id,expert,cadet,3,1,cursor))+
                                '\nСтратегия: '+str(GetMarkInVoting(voting_id,expert,cadet,3,2,cursor))+
                                '\nУправляемость: '+str(GetMarkInVoting(voting_id,expert,cadet,3,3,cursor)),
                                reply_markup=config.ChooseKeyboardForAuthority(voting_id, cadet), parse_mode='HTML')
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # commenting(expert,cadet,voting_id,3)
        AcceptMark(voting_id, expert, cadet, 3, cursor, db)
        cadets = GetNonvotedCadetsForExpert(voting_id, '@'+call.from_user.username, 3, cursor)
        if cadets is None or len(cadets) == 0:
            bot.send_message(call.message.chat.id, 'Спасибо за ваши оценки, ваше голосование по оси власти окончено')
            if IsVotingFinished(voting_id, 3, cursor):
                CompileMarksByAxis(voting_id, 3, cursor, db)
                cursor.execute('SELECT voting_date FROM votings WHERE id=' + str(voting_id))
                time = cursor.fetchone()[0]
                marks = GetMarksForDate(time, 3, cursor)
                cur_cadet = marks[0][0]
                result = '<b>Результаты оценки по оси власти в проекте "' + GetProjectTitle(project_id, cursor) \
                         + '"</b>\nКурсант: <b>' + GetName(cur_cadet, cursor) + '</b>\n'
                FinishVoting(voting_id, cursor, db)
                for mark in marks:
                    if mark[0] == cur_cadet:
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Самоуправление'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Стратегия'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Управляемость'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                    else:
                        cur_cadet = mark[0]
                        result += '\nКурсант: <b>' + GetName(mark[0], cursor) + '</b>\n'
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Самоуправление'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Стратегия'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Управляемость'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                members = GetMembersOfProject(project_id, cursor)
                experts = GetExpertsFromVoting(voting_id, 3, cursor)
                for member in members:
                    bot.send_message(GetChatId(member[0], cursor), result, parse_mode='HTML')
                for expert in experts:
                    bot.send_message(GetChatId(expert[0], cursor), result, parse_mode='HTML')
        else:
            cadet = cadets[0][0]
            bot.send_message(GetChatId(expert, cursor),
                             'Оценка нематериального вклада\nПроект <b>"' + GetProjectTitle(project_id, cursor) +
                             '"</b>\nОсь власти\nКурсант: <b>' + GetName(cadet, cursor) +
                             '</b>\nСамоуправление: 0\nСтратегия: 0\nУправляемость: 0',
                             reply_markup=config.ChooseKeyboardForAuthority(voting_id, cadet), parse_mode='HTML')


def commenting(expert,cadet,voting_id,axis):
    first_mark = GetMarkInVoting(voting_id, expert, cadet, axis, 1, cursor)
    second_mark = GetMarkInVoting(voting_id, expert, cadet, axis, 2, cursor)
    third_mark = GetMarkInVoting(voting_id, expert, cadet, axis, 3, cursor)
    if axis == 1:
        bot.send_message(GetChatId(expert, cursor),'Вы оценили материальный вклад курсанта <b>'
                         +GetName(cadet,cursor)+'</b> по оси отношений. \nВаши оценки:\nЛичностное развитие:<b>' + str(first_mark) +
                         '</b>\nПонятность: <b>'+str(second_mark) +
                         '</b>\nЭнергия: <b>'+str(third_mark) + '</b>\nПожалуйста, прокомментируйте ваше решение', parse_mode='HTML')
        SetState(expert, 81, cursor, db)
    elif axis == 2:
        bot.send_message(GetChatId(expert, cursor), 'Вы оценили материальный вклад курсанта <b>'
                         + GetName(cadet, cursor) + '</b> по оси дела. Ваши оценки:\nДвижение:<b>' + str(
            first_mark) +
                         '</b>\nЗавершенность: <b>' + str(second_mark) +
                         '</b>\nПодтверждение средой: <b>' + str(third_mark) +
                         '/<b>\nПожалуйста, прокомментируйте ваше решение', parse_mode='HTML')
        SetState(expert, 82, cursor, db)
    else:
        bot.send_message(GetChatId(expert, cursor), 'Вы оценили материальный вклад курсанта <b>'
                         + GetName(cadet, cursor) + '</b> по оси власти. Ваши оценки:\nСамоуправление:<b>' + str(
            first_mark) +
                         '</b>\nСтратегия: <b>' + str(second_mark) +
                         '</b>\nУправляемость: <b>' + str(third_mark) +
                         '</b>\nПожалуйста, прокомментируйте ваше решение', parse_mode='HTML')
        SetState(expert, 83, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 81)
def comment_relations(message):
    pass