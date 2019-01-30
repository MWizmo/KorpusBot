# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
from db_commands.db_voting import *
import telebot
from config import bot, db, cursor, get_keyboard

def put_sign(num):
    if num == 0:
        return '-'
    else:
        return '+'

# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('relations'))
# def fighters_vote(call):
#     if call.data[-1] != "5":
#         if call.data[-1] == "1":
#             config.project_relation_marks[call.from_user.username][0] = 1 if \
#             config.project_relation_marks[call.from_user.username][0] == 0 else 0
#         elif call.data[-1] == "2":
#             config.project_relation_marks[call.from_user.username][1] = 1 if \
#             config.project_relation_marks[call.from_user.username][1] == 0 else 0
#         elif call.data[-1] == "3":
#             config.project_relation_marks[call.from_user.username][2] = 1 if \
#             config.project_relation_marks[call.from_user.username][2] == 0 else 0
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь отношений\nКурсант: ' +
#                                    GetName('@' + call.from_user.username,cursor) +
#                                    '\nЛичностное развитие: ' + put_sign(config.project_relation_marks[call.from_user.username][0]) +
#                                    '\nПонятность: ' + put_sign(config.project_relation_marks[ call.from_user.username][1]) +
#                                    '\nЭнергия: ' + put_sign(config.project_relation_marks[call.from_user.username][2]),
#                               reply_markup=config.ChooseKeyboardForRelations())
#     else:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         id = config.project_relation_marks[call.from_user.username][3]
#         project_members = GetMembersOfProject(id,cursor)
#         # AddMark('@' + call.from_user.username, config.project_relation_marks[call.from_user.username][:3], 1,len(project_members)-1, cursor,db)
#         keyboard = telebot.types.InlineKeyboardMarkup()
#         keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%'+str(id)+'%@'+call.from_user.username+'%1%1'),
#                      telebot.types.InlineKeyboardButton(text='Не согласен',callback_data='decide_vote%' + str(id) + '%@' + call.from_user.username + '%2%1'))
#         for member in project_members:
#             if member[0]!='@'+call.from_user.username:
#                 bot.send_message(GetChatId(member[0],cursor),'Курсант '+GetName('@'+call.from_user.username,cursor)+
# 				' оценил себя по оси отношений в рамках проекта "' + GetProjectTitle(id,cursor) +
#                                  '". Вот его оценки:\n Личностное развитие: ' +
#                                  str(config.project_relation_marks[call.from_user.username][0]) +
#                                  '\n Понятность: ' + str(config.project_relation_marks[ call.from_user.username][1]) +
#                                  '\n Энергия: ' + str(config.project_relation_marks[call.from_user.username][2]) +'\nВы согласны с этими оценками?',
#                                  reply_markup=keyboard)
#                 StartEvaluateInProject(int(id),'@'+call.from_user.username,1,config.project_relation_marks[call.from_user.username][:3],member,cursor,db)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))
#
#
# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('business'))
# def educator_votes(call):
#     if call.data[-1] != '5':
#         if call.data[-1] == '1':
#             config.project_business_marks[call.from_user.username][0] = 1 \
#                 if config.project_business_marks[call.from_user.username][0] == 0 else 0
#         if call.data[-1] == '2':
#             config.project_business_marks[call.from_user.username][1] = 1 \
#                 if config.project_business_marks[call.from_user.username][1] == 0 else 0
#         if call.data[-1] == '3':
#             config.project_business_marks[call.from_user.username][2] = 1 \
#                 if config.project_business_marks[call.from_user.username][2] == 0 else 0
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь дела \nКурсант: ' +
#                                    GetName('@' + call.from_user.username,cursor) +
#                                    '\nДвижение: ' + put_sign(config.project_business_marks[call.from_user.username][0]) + '\nЗавершенность: ' +
#                                    put_sign(config.project_business_marks[call.from_user.username][1]) +
#                                    '\nПодтверждение средой: ' + put_sign(config.project_business_marks[call.from_user.username][2]),
#                               reply_markup=config.ChooseKeyboardForBusiness())
#     else:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         id = config.project_business_marks[call.from_user.username][3]
#         project_members = GetMembersOfProject(id, cursor)
#         # AddMark('@' + call.from_user.username, config.project_business_marks[call.from_user.username][:3], 2,
#         #         len(project_members)-1, cursor, db)
#         keyboard = telebot.types.InlineKeyboardMarkup()
#         keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%' + str(
#             id) + '%@' + call.from_user.username + '%1%2'),
#                      telebot.types.InlineKeyboardButton(text='Не согласен', callback_data='decide_vote%' + str(
#                          id) + '%@' + call.from_user.username + '%2%2'))
#         for member in project_members:
#             if member[0]!='@'+call.from_user.username:
#                 bot.send_message(GetChatId(member[0], cursor), 'Курсант ' + GetName('@' + call.from_user.username, cursor) +
#                                  ' оценил себя по оси дела в рамках проекта "' + GetProjectTitle(id,cursor) +
#                                  '". Вот его оценки:\n Движение: ' +
#                                  str(config.project_business_marks[call.from_user.username][0]) +
#                                  '\n Завершенность: ' + str(config.project_business_marks[call.from_user.username][1]) +
#                                  '\n Подтверждение средой: ' +
#                                  str(config.project_business_marks[call.from_user.username][2]) + '\nВы согласны с этими оценками?',
#                                  reply_markup=keyboard)
#                 StartEvaluateInProject(int(id), '@' + call.from_user.username, 2,config.project_business_marks[call.from_user.username][:3], member, cursor, db)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))
#
#
# @bot.callback_query_handler(func=lambda call: True and call.data.startswith('authority'))
# def authority_votes1(call):
#     if call.data[-1] != '5':
#         if call.data[-1] == '1':
#             config.project_authority_marks[call.from_user.username][0] = 1 \
#                 if config.project_authority_marks[call.from_user.username][0] == 0 else 0
#         if call.data[-1] == '2':
#             config.project_authority_marks[call.from_user.username][1] = 1 \
#                 if config.project_authority_marks[call.from_user.username][1] == 0 else 0
#         if call.data[-1] == '3':
#             config.project_authority_marks[call.from_user.username][2] = 1 \
#                 if config.project_authority_marks[call.from_user.username][2] == 0 else 0
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                               text='Оценка нематериального вклада.\nОсь власти \nКурсант: ' +
#                                    GetName('@'+call.from_user.username,cursor) +
#                                    '\nСамоуправление: ' + put_sign(config.project_authority_marks[call.from_user.username][0]) +
#                                    '\nСтратегия: ' + put_sign(config.project_authority_marks[call.from_user.username][1]) +
#                                    '\nУправляемость: ' + put_sign(config.project_authority_marks[call.from_user.username][2]),
#                               reply_markup=config.ChooseKeyboardForAuthority())
#     else:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         id = config.project_authority_marks[call.from_user.username][3]
#         project_members = GetMembersOfProject(id, cursor)
#         # AddMark('@' + call.from_user.username, config.project_authority_marks[call.from_user.username][:3], 3,
#          #       len(project_members)-1, cursor, db)
#         keyboard = telebot.types.InlineKeyboardMarkup()
#         keyboard.row(telebot.types.InlineKeyboardButton(text='Согласен', callback_data='decide_vote%' + str(
#             id) + '%@' + call.from_user.username + '%1%3'),
#                      telebot.types.InlineKeyboardButton(text='Не согласен', callback_data='decide_vote%' + str(
#                          id) + '%@' + call.from_user.username + '%2%3'))
#         for member in project_members:
#             if member[0]!='@'+call.from_user.username:
#                 bot.send_message(GetChatId(member[0], cursor), 'Курсант ' + GetName('@' + call.from_user.username, cursor) +
#                                  ' оценил себя по оси власти в рамках проекта "' + GetProjectTitle(id,cursor) +
#                                  '". Вот его оценки:\n Самоуправление: ' +
#                                  str(config.project_authority_marks[call.from_user.username][0]) +
#                                  '\n Стратегия: ' + str(config.project_authority_marks[call.from_user.username][1]) +
#                                  '\n Управляемость: ' +
#                                  str(config.project_authority_marks[call.from_user.username][2]) + '\nВы согласны с этими оценками?',
#                                  reply_markup=keyboard)
#         bot.send_message(call.message.chat.id, 'Оценивание завершено',reply_markup=get_keyboard('@' + call.from_user.username))
