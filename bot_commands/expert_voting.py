# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_expert_voting import *
from db_commands.db_projects import IsUserTeamlead
from db_commands.db_marks import *
import telebot
import re
from config import bot, db, cursor, get_keyboard
import config


def start_expert_voting(message):
    if IsThereActiveVoting(cursor):
        bot.send_message(message.chat.id, 'В данное время уже идет оценка экспертов')
    else:
        if GetCurrentPreparingExpertVoting(cursor) is None:
            bot.send_message(message.chat.id, 'Введите предполагаемую дату и время оценки в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')
            SetState('@'+message.from_user.username, 911, cursor, db)
        else:
            expert_voting_menu('@'+message.from_user.username, GetCurrentPreparingExpertVoting(cursor)[0])


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 911)
def set_date(message):
    time = message.text
    if re.fullmatch(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', time):
        bot.send_message(message.chat.id, 'Спасибо, время зафиксировано')
        SetState('@' + message.from_user.username, 6, cursor, db)
        OrganizeExpertVoting(time, cursor, db)
        id = GetCurrentPreparingExpertVoting(cursor)[0]
        AddTeamleadToVoting(id, '@'+message.from_user.username, cursor, db)
        users = GetListOfUsers(cursor)
        for user in users:
            if IsUserTeamlead(user[0], cursor) and user[0] != '@'+message.from_user.username:
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(telebot.types.InlineKeyboardButton(text='Принять',
                                                                callback_data='teamlead_decide%1%' + str(id)),
                             telebot.types.InlineKeyboardButton(text='Отклонить',
                                                                callback_data='teamlead_decide%2%' + str(id)))
                bot.send_message(GetChatId(user[0], cursor), GetName('@'+message.from_user.username, cursor) +
                                 ' инициировал оценку экспертов. Предполагаемая дата оценки: ' + time,
                                 reply_markup=keyboard)
        bot.send_message(message.chat.id, 'Всем тимлидам высланы оповещения о предстоящей оценке')
        expert_voting_menu('@'+message.from_user.username, id)
    else:
        bot.send_message(message.chat.id, 'Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('teamlead_decide'))
def accept(call):
    items = call.data.split('%')
    if items[1] == '1':
        AddTeamleadToVoting(items[2], '@'+call.from_user.username, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, 'Спасибо, ваше мнение учтено')


def GetNumberOfTeamleads():
    users = GetListOfUsers(cursor)
    num = 0
    for user in users:
        if IsUserTeamlead(user[0], cursor):
            num += 1
    return num


def expert_voting_menu(user_nick, voting_id):
    mess = 'Оценка экспертов\nДата оценки: ' + GetDateOfPreparingExpertVoting(cursor)
    mess += '\nНа данный момент подтвердили свое участие ' + str(GetNumberOfAcceptedTeamleads(voting_id, cursor)) + ' из ' + str(GetNumberOfTeamleads())
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Изменить дату оценки', callback_data='change_date'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Начать оценку', callback_data='start_expert_voting'))
    bot.send_message(GetChatId(user_nick, cursor), mess, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('change_date'))
def change_date(call):
    bot.send_message(call.message.chat.id,
                     'Введите предполагаемую дату и время оценки в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')
    SetState('@' + call.from_user.username, 9111, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 9111)
def chang_date(message):
    time = message.text
    if re.fullmatch(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', time):
        bot.send_message(message.chat.id, 'Время оценки изменено')
        SetState('@' + message.from_user.username, 6, cursor, db)
        ChangeDate(time, cursor, db)
        expert_voting_menu('@' + message.from_user.username, GetCurrentPreparingExpertVoting(cursor)[0])
    else:
        bot.send_message(message.chat.id, 'Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ (пример: 01.01.2019 13:30)')


def GetExperts():
    users = GetListOfUsers(cursor)
    experts = list()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [10]):
            experts.append(user[0])
    return experts

@bot.callback_query_handler(func=lambda call: True and call.data.startswith('start_expert_voting'))
def start(call):
    id = GetCurrentPreparingExpertVoting(cursor)[0]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    percent = float(GetNumberOfAcceptedTeamleads(id, cursor)) / float(GetNumberOfTeamleads())
    print(percent)
    if percent <= 0.5:
        bot.send_message(call.message.chat.id,
                         'Пока невозможно начать оценку, т.к. недостаточно тимлидов согласились на участие')
        expert_voting_menu('@' + call.from_user.username, id)
    else:
        ChangeVotingStatus('Started', id, cursor, db)
        teamleads = GetListOfAcceptedTeamleads(id, cursor)
        experts = GetExperts()
        StartExpertVoting(id, experts, teamleads, cursor, db)
        for teamlead in teamleads:
            expert = GetNextExpertForVoting(teamlead[0], id, cursor)
            mess = 'Оценивание экспертов\nЭксперт: ' + GetName(expert, cursor) + '\nДвижение:0\nЗавершенность:0\nПодтверждение средой:0'
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="Движение", callback_data="exp_bus%1%"
                                                                                           + str(id) + "%" + expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Завершенность", callback_data="exp_bus%2%"
                                                                                                + str(id) + "%" + expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Подтверждение средой", callback_data="exp_bus%3%"
                                                                                                       + str(id) + "%"+expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="exp_bus%4%"
                                                                                                       + str(id) + "%"+expert))
            bot.send_message(GetChatId(teamlead[0], cursor), mess, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('exp_bus'))
def lead_votes(call):
    items = call.data.split('%')
    criterion = items[1]
    id = items[2]
    expert = items[3]
    lead = '@' + call.from_user.username
    if criterion == '4':
        AcceptMark(lead, id, expert, cursor, db)
        expert = GetNextExpertForVoting(lead, id, cursor)
        if expert == 0:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(GetChatId(lead, cursor), 'Вы оценили всех экспертов. Спасибо за участие')
            if IsVotingFinished(id, cursor):
                bot.send_message(GetChatId(lead, cursor), 'Оценивание завершено')
                teamleads = GetListOfAcceptedTeamleads(id, cursor)
                experts = GetExperts()
                CompileMarksOfExperts(id, experts, teamleads, cursor, db)
                cursor.execute('SELECT voting_date FROM expert_voting WHERE id=' + str(id))
                time = cursor.fetchone()[0]
                marks = GetAllExpertsMarksForDate(time, cursor)
                cur_expert = marks[0][0]
                result = '<b>Результаты оценки</b>\nЭксперт: <b>' + GetName(cur_expert, cursor) + '</b>\n'
                ChangeVotingStatus('Finished', id, cursor, db)
                for mark in marks:
                    if mark[0] == cur_expert:
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Движение'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Завершенность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Подтверждение средой'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                    else:
                        cur_expert = mark[0]
                        result += '\nЭксперт: <b>' + GetName(mark[0], cursor) + '</b>\n '
                        if mark[1] == '1' or mark[1] == 1:
                            result += 'Движение'
                        elif mark[1] == '2' or mark[1] == 2:
                            result += 'Завершенность'
                        elif mark[1] == '3' or mark[1] == 3:
                            result += 'Подтверждение средой'
                        result += ': <b>' + str(mark[2]) + '</b>\n'
                for teamlead in teamleads:
                    bot.send_message(GetChatId(teamlead[0], cursor), result, parse_mode='HTML')
        else:
            mess = 'Оценивание экспертов\nЭксперт: ' + GetName(expert, cursor) + '\nДвижение:' + \
                   str(GetMarkForTeamLeadOf(lead, id, expert, 1, cursor)) + '\nЗавершенность:' + \
                   str(GetMarkForTeamLeadOf(lead, id, expert, 2, cursor)) + '\nПодтверждение средой:' + \
                   str(GetMarkForTeamLeadOf(lead, id, expert, 3, cursor))
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="Движение", callback_data="exp_bus%1%"
                                                                                           + str(id) + "%" + expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Завершенность", callback_data="exp_bus%2%"
                                                                                                + str(
                id) + "%" + expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Подтверждение средой", callback_data="exp_bus%3%"
                                                                                                       + str(
                id) + "%" + expert))
            keyboard.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="exp_bus%4%"
                                                                                            + str(id) + "%" + expert))
            # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            #bot.send_message(GetChatId(lead, cursor), mess, reply_markup=keyboard)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=mess, reply_markup=keyboard)
    else:
        PutMarkForTeamLeadOf(lead, id, expert, criterion, cursor, db)
        mess = 'Оценивание экспертов\nЭксперт: ' + GetName(expert, cursor) + '\nДвижение:' +\
               str(GetMarkForTeamLeadOf(lead, id, expert, 1, cursor))+'\nЗавершенность:' + \
               str(GetMarkForTeamLeadOf(lead, id, expert, 2, cursor))+'\nПодтверждение средой:' +\
               str(GetMarkForTeamLeadOf(lead, id, expert, 3, cursor))
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="Движение", callback_data="exp_bus%1%"
                                                                                       + str(id) + "%" + expert))
        keyboard.add(telebot.types.InlineKeyboardButton(text="Завершенность", callback_data="exp_bus%2%"
                                                                                            + str(id) + "%" + expert))
        keyboard.add(telebot.types.InlineKeyboardButton(text="Подтверждение средой", callback_data="exp_bus%3%"
                                                                                                   + str(
            id) + "%" + expert))
        keyboard.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="exp_bus%4%"
                                                                                        + str(id) + "%" + expert))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(GetChatId(lead, cursor), mess, reply_markup=keyboard)
