# -*- coding: utf-8 -*-
import db_commands.db_users as db_users
import telebot
import sqlite3
from emoji import emojize
import bot_token
import pymysql

bot = telebot.TeleBot(bot_token.token)
#db = sqlite3.connect("korpus.db", check_same_thread=False)
db = pymysql.connect("localhost", "root", "1", "korpus", charset="utf8")
cursor = db.cursor()
# db.close()

def isRang(a, b):
    c = list(set(a) & set(b))
    return len(c) > 0


def get_keyboard(id):
    rangs = db_users.GetRangs(id, cursor)
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(emojize(":bar_chart: Оценки", use_aliases=True),
               emojize(':open_file_folder: Проекты', use_aliases=True),
               emojize(':clipboard: Профиль', use_aliases=True))
    if isRang(rangs, [5]):
        markup.add('Функции тьютора')
    if isRang(rangs, [9]):
        markup.add(emojize(':necktie: Функции администратора'))
    if isRang(rangs, [8]):
        markup.row(emojize(':credit_card: Функции инвестора'))
    markup.row(emojize(':globe_with_meridians: Токены'))
    return markup

# ---Variables---
current_user_for_dossier = ''

project_relation_marks = dict()
project_business_marks = dict()
project_authority_marks = dict()

fighters_num=0
fighters_list=[]
fighters_marks={}

current_fighter_for_business=0
current_fighter_for_authority=0

business_marks=[]
authority_first_marks=[]
authority_second_marks=[]

budget=0
second_flow_list=[]
second_flow_num=0
current_fighter_for_tutor=0
tutor_marks=[]
current_fighter_for_expert=0
expert_marks=[]

project_members=[]
current_project_member=0
project_marks=[]
current_project=''
#----------

#-----Feybpards------

keyboard_axis_of_relations_finish=telebot.types.InlineKeyboardMarkup()
keyboard_axis_of_relations_finish.add(telebot.types.InlineKeyboardButton(text="Личностный рост", callback_data="relations_1"))
keyboard_axis_of_relations_finish.add(telebot.types.InlineKeyboardButton(text="Ясность позиции", callback_data="relations_2"))
keyboard_axis_of_relations_finish.add(telebot.types.InlineKeyboardButton(text="Энергия", callback_data="relations_3"))
keyboard_axis_of_relations_finish.add(telebot.types.InlineKeyboardButton(text="Завершить оценивание", callback_data="relations_5"))


keyboard_axis_of_business_finish=telebot.types.InlineKeyboardMarkup()
keyboard_axis_of_business_finish.add(telebot.types.InlineKeyboardButton(text="Движение", callback_data="business_1"))
keyboard_axis_of_business_finish.add(telebot.types.InlineKeyboardButton(text="Завершенность", callback_data="business_2"))
keyboard_axis_of_business_finish.add(telebot.types.InlineKeyboardButton(text="Подтверждение средой", callback_data="business_3"))
keyboard_axis_of_business_finish.add(telebot.types.InlineKeyboardButton(text="Завершить оценивание", callback_data="business_5"))


keyboard_axis_of_authority_finish=telebot.types.InlineKeyboardMarkup()
keyboard_axis_of_authority_finish.add(telebot.types.InlineKeyboardButton(text="Самоуправление", callback_data="authority_1"))
keyboard_axis_of_authority_finish.add(telebot.types.InlineKeyboardButton(text="Стратегия", callback_data="authority_2"))
keyboard_axis_of_authority_finish.add(telebot.types.InlineKeyboardButton(text="Управляемость", callback_data="authority_3"))
keyboard_axis_of_authority_finish.add(telebot.types.InlineKeyboardButton(text="Завершить оценивание", callback_data="authority_5"))
#----------

def ChooseKeyboardForRelations(voting_id, cadet, is_last):
    keyboard_axis_of_relations = telebot.types.InlineKeyboardMarkup()
    keyboard_axis_of_relations.row(telebot.types.InlineKeyboardButton(text="Личностный рост", callback_data="relations%1%"+str(voting_id)+"%"+str(cadet)))
                                   #telebot.types.InlineKeyboardButton(text='?', callback_data='relations%7'))
    keyboard_axis_of_relations.row(telebot.types.InlineKeyboardButton(text="Ясность позиции", callback_data="relations%2%"+str(voting_id)+"%"+str(cadet)))
                                   #telebot.types.InlineKeyboardButton(text='?', callback_data='relations%8'))
    keyboard_axis_of_relations.row(telebot.types.InlineKeyboardButton(text="Энергия", callback_data="relations%3%"+str(voting_id)+"%"+str(cadet)))
                                   #telebot.types.InlineKeyboardButton(text='?', callback_data='relations%9'))
    # keyboard_axis_of_relations.add(telebot.types.InlineKeyboardButton(text="Изменить предыдущие оценки",
    #                                                                   callback_data="relations%5%" + str(
    #                                                                       voting_id) + "%" + str(cadet)))
    if is_last == False:
        keyboard_axis_of_relations.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="relations%4%"+str(voting_id)+"%"+str(cadet)))
    else:
        keyboard_axis_of_relations.add(telebot.types.InlineKeyboardButton(text="Завершить",
                                                                          callback_data="relations%4%" + str(
                                                                              voting_id) + "%" + str(cadet)))
    return keyboard_axis_of_relations


def ChooseKeyboardForBusiness(voting_id, cadet, is_last):
    keyboard_axis_of_business = telebot.types.InlineKeyboardMarkup()
    keyboard_axis_of_business.row(telebot.types.InlineKeyboardButton(text="Движение", callback_data="business%1%"+str(voting_id)+"%"+str(cadet)))
                                  #telebot.types.InlineKeyboardButton(text='?', callback_data='business%7'))
    keyboard_axis_of_business.row(telebot.types.InlineKeyboardButton(text="Завершенность", callback_data="business%2%"+str(voting_id)+"%"+str(cadet)))
                                  #telebot.types.InlineKeyboardButton(text='?', callback_data='business%8'))
    keyboard_axis_of_business.row(
        telebot.types.InlineKeyboardButton(text="Подтверждение средой", callback_data="business%3%"+str(voting_id)+"%"+str(cadet)))
        #telebot.types.InlineKeyboardButton(text='?', callback_data='business%9'))
    # keyboard_axis_of_business.add(telebot.types.InlineKeyboardButton(text="Ищменить предыдущие оценки",
    #                                                                  callback_data="business%5%" + str(
    #                                                                      voting_id) + "%" + str(cadet)))
    if is_last == False:
        keyboard_axis_of_business.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="business%4%"+str(voting_id)+"%"+str(cadet)))
    else:
        keyboard_axis_of_business.add(telebot.types.InlineKeyboardButton(text="Завершить",
                                                                         callback_data="business%4%" + str(
                                                                             voting_id) + "%" + str(cadet)))
    return keyboard_axis_of_business


def ChooseKeyboardForAuthority(voting_id, cadet, is_last):
    keyboard_axis_of_authority = telebot.types.InlineKeyboardMarkup()
    keyboard_axis_of_authority.row(
        telebot.types.InlineKeyboardButton(text="Самоуправление", callback_data="authority%1%"+str(voting_id)+"%"+str(cadet)))
        #telebot.types.InlineKeyboardButton(text='?', callback_data='authority%7'))
    keyboard_axis_of_authority.row(telebot.types.InlineKeyboardButton(text="Стратегия", callback_data="authority%2%"+str(voting_id)+"%"+str(cadet)))
                                   #telebot.types.InlineKeyboardButton(text='?', callback_data='authority%8'))
    keyboard_axis_of_authority.row(
        telebot.types.InlineKeyboardButton(text="Управляемость", callback_data="authority%3%"+str(voting_id)+"%"+str(cadet)))
        #telebot.types.InlineKeyboardButton(text='?', callback_data='authority%9'))
    # keyboard_axis_of_authority.add(telebot.types.InlineKeyboardButton(text="Изменить предыдущие оценки",
    #                                                                   callback_data="authority%5%" + str(
    #                                                                       voting_id) + "%" + str(cadet)))
    if is_last == False:
        keyboard_axis_of_authority.add(telebot.types.InlineKeyboardButton(text="Следующий", callback_data="authority%4%"+str(voting_id)+"%"+str(cadet)))
    else:
        keyboard_axis_of_authority.add(telebot.types.InlineKeyboardButton(text="Завершить",
                                                                          callback_data="authority%4%" + str(
                                                                              voting_id) + "%" + str(cadet)))
    return keyboard_axis_of_authority
