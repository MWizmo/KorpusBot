# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_marks import *
import telebot
from config import bot, db, cursor, get_keyboard, isRang

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
