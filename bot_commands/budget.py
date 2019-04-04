# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_budget import *
from db_commands.db_marks import GetAllMarks
import telebot
from config import bot, db, cursor, get_keyboard, isRang
import config

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
