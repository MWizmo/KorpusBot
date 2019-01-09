# -*- coding: utf-8 -*-
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import db_commands
import telebot
import sqlite3
from emoji import emojize

# token = '644032287:AAECDJ2hZJfNJnZcsuahPCoqyrx0lGQI6d8'  # main bot
token = '573817226:AAHM6cFFyr64GS7c5ZWw6z_j6UHGNKQldBU' #second bot
# token = '691001400:AAF1zCuHnCpt3scH8_U1G3bNmMfbnLceW0g'

bot = telebot.TeleBot(token)
db = sqlite3.connect("korpus.db", check_same_thread=False)
cursor = db.cursor()


def isRang(a, b):
    c = list(set(a) & set(b))
    return len(c) > 0

def get_keyboard(nick):
    rangs = db_commands.GetRangs(nick,cursor)
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

#-----First flow------
keyboard_axis_of_relations=InlineKeyboardMarkup()
keyboard_axis_of_relations.add(InlineKeyboardButton(text="Личностное развитие", callback_data="relations_1"))
keyboard_axis_of_relations.add(InlineKeyboardButton(text="Понятность", callback_data="relations_2"))
keyboard_axis_of_relations.add(InlineKeyboardButton(text="Энергия", callback_data="relations_3"))
keyboard_axis_of_relations.add(InlineKeyboardButton(text="Следующий", callback_data="relations_4"))

keyboard_axis_of_relations_finish=InlineKeyboardMarkup()
keyboard_axis_of_relations_finish.add(InlineKeyboardButton(text="Личностное развитие", callback_data="relations_1"))
keyboard_axis_of_relations_finish.add(InlineKeyboardButton(text="Понятность", callback_data="relations_2"))
keyboard_axis_of_relations_finish.add(InlineKeyboardButton(text="Энергия", callback_data="relations_3"))
keyboard_axis_of_relations_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="relations_5"))

keyboard_axis_of_business=InlineKeyboardMarkup()
keyboard_axis_of_business.add(InlineKeyboardButton(text="Движение", callback_data="business_1"))
keyboard_axis_of_business.add(InlineKeyboardButton(text="Завершенность", callback_data="business_2"))
keyboard_axis_of_business.add(InlineKeyboardButton(text="Подтверждение средой", callback_data="business_3"))
keyboard_axis_of_business.add(InlineKeyboardButton(text="Следующий", callback_data="business_4"))

keyboard_axis_of_business_finish=InlineKeyboardMarkup()
keyboard_axis_of_business_finish.add(InlineKeyboardButton(text="Движение", callback_data="business_1"))
keyboard_axis_of_business_finish.add(InlineKeyboardButton(text="Завершенность", callback_data="business_2"))
keyboard_axis_of_business_finish.add(InlineKeyboardButton(text="Подтверждение средой", callback_data="business_3"))
keyboard_axis_of_business_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="business_5"))

keyboard_axis_of_authority=InlineKeyboardMarkup()
keyboard_axis_of_authority.add(InlineKeyboardButton(text="Самоуправление", callback_data="authority_1"))
keyboard_axis_of_authority.add(InlineKeyboardButton(text="Стратегия", callback_data="authority_2"))
keyboard_axis_of_authority.add(InlineKeyboardButton(text="Управляемость", callback_data="authority_3"))
keyboard_axis_of_authority.add(InlineKeyboardButton(text="Следующий", callback_data="authority_4"))

keyboard_axis_of_authority_finish=InlineKeyboardMarkup()
keyboard_axis_of_authority_finish.add(InlineKeyboardButton(text="Самоуправление", callback_data="authority_1"))
keyboard_axis_of_authority_finish.add(InlineKeyboardButton(text="Стратегия", callback_data="authority_2"))
keyboard_axis_of_authority_finish.add(InlineKeyboardButton(text="Управляемость", callback_data="authority_3"))
keyboard_axis_of_authority_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="authority_5"))
#----------

def ChooseKeyboardForRelations():
    return keyboard_axis_of_relations_finish

def ChooseKeyboardForBusiness():
    return keyboard_axis_of_business_finish

def ChooseKeyboardForAuthority():
    return keyboard_axis_of_authority_finish


