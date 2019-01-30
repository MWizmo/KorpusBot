# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_tokens import *
import telebot
from config import bot, db, cursor, get_keyboard

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