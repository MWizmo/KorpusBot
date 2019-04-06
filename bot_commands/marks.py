# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_marks import *
import telebot
from config import bot, db, cursor, get_keyboard, isRang


def marks_of(message, user):
    dates = GetAllDatesOfVotingByUser(user, cursor)
    info = ''
    if len(dates) > 0:
        for date in dates:
            info += '<b>' + date[0] + '</b>\n'
            marks = GetMarksForDateAndUser(date[0], 1, user, cursor)
            info += '<b>Ось отношений:</b>\n'
            for mark in marks:
                if mark[0] == '1' or mark[0] == 1:
                    info += '  Личностное развитие'
                elif mark[0] == '2' or mark[0] == 2:
                    info += '  Понятность'
                elif mark[0] == '3' or mark[0] == 3:
                    info += '  Энергия'
                info += ': <b>' + str(mark[1]) + '</b>\n'
            marks = GetMarksForDateAndUser(date[0], 2, user, cursor)
            info += '<b>Ось дела:</b>\n'
            for mark in marks:
                if mark[0] == '1' or mark[0] == 1:
                    info += '  Движение'
                elif mark[0] == '2' or mark[0] == 2:
                    info += '  Завершенность'
                elif mark[0] == '3' or mark[0] == 3:
                    info += '  Подтверждение средой'
                info += ': <b>' + str(mark[1]) + '</b>\n'
            marks = GetMarksForDateAndUser(date[0], 3, user, cursor)
            info += '<b>Ось власти:</b>\n'
            for mark in marks:
                if mark[0] == '1' or mark[0] == 1:
                    info += '  Самоуправление'
                elif mark[0] == '2' or mark[0] == 2:
                    info += '  Стратегия'
                elif mark[0] == '3' or mark[0] == 3:
                    info += '  Управляемость'
                info += ': <b>' + str(mark[1]) + '</b>\n'
        bot.send_message(message.chat.id, info, parse_mode='HTML')
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
        dates = GetAllDatesOfVotingByUser(user, cursor)
        info = ''
        if len(dates) > 0:
            for date in dates:
                info += '<b>' + date[0] + '</b>\n'
                marks = GetMarksForDateAndUser(date[0], 1, user, cursor)
                info += '<b>Ось отношений:</b>\n'
                for mark in marks:
                    if mark[0] == '1' or mark[0] == 1:
                        info += '  Личностное развитие'
                    elif mark[0] == '2' or mark[0] == 2:
                        info += '  Понятность'
                    elif mark[0] == '3' or mark[0] == 3:
                        info += '  Энергия'
                    info += ': <b>' + str(mark[1]) + '</b>\n'
                marks = GetMarksForDateAndUser(date[0], 2, user, cursor)
                info += '<b>Ось дела:</b>\n'
                for mark in marks:
                    if mark[0] == '1' or mark[0] == 1:
                        info += '  Движение'
                    elif mark[0] == '2' or mark[0] == 2:
                        info += '  Завершенность'
                    elif mark[0] == '3' or mark[0] == 3:
                        info += '  Подтверждение средой'
                    info += ': <b>' + str(mark[1]) + '</b>\n'
                marks = GetMarksForDateAndUser(date[0], 3, user, cursor)
                info += '<b>Ось власти:</b>\n'
                for mark in marks:
                    if mark[0] == '1' or mark[0] == 1:
                        info += '  Самоуправление'
                    elif mark[0] == '2' or mark[0] == 2:
                        info += '  Стратегия'
                    elif mark[0] == '3' or mark[0] == 3:
                        info += '  Управляемость'
                    info += ': <b>' + str(mark[1]) + '</b>\n'
            bot.send_message(call.message.chat.id, info, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Для данного пользователя пока нет оценок',
                             reply_markup=get_keyboard('@' + call.from_user.username))
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard('@' + call.from_user.username))
