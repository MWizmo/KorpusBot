# -*- coding: utf-8 -*-
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import db_commands

token = '644032287:AAECDJ2hZJfNJnZcsuahPCoqyrx0lGQI6d8'
# token = '573817226:AAHM6cFFyr64GS7c5ZWw6z_j6UHGNKQldBU'

# ---Variables---
fighters_num=0
fighters_list=[]
fighters_marks={}

current_fighter_for_educator=0
current_fighter_for_authority=0
current_second_flow_for_authority=0

educator_marks=[]
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
keyboard_axis_of_relations_first=InlineKeyboardMarkup()
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Честность", callback_data="first_flow_relations_1"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Ясность позиции", callback_data="first_flow_relations_2"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Уровень энергии", callback_data="first_flow_relations_3"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Устойчивость личностного роста", callback_data="first_flow_relations_4"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Интенсивность личностного роста", callback_data="first_flow_relations_5"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="first_flow_relations_6"))
keyboard_axis_of_relations_first.add(InlineKeyboardButton(text="Следующий", callback_data="first_flow_relations_7"))

keyboard_axis_of_relations_first_finish=InlineKeyboardMarkup()
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Честность", callback_data="first_flow_relations_1"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Ясность позиции", callback_data="first_flow_relations_2"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Уровень энергии", callback_data="first_flow_relations_3"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Устойчивость личностного роста", callback_data="first_flow_relations_4"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Интенсивность личностного роста", callback_data="first_flow_relations_5"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="first_flow_relations_6"))
keyboard_axis_of_relations_first_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="first_flow_relations_8"))

keyboard_axis_of_business_first=InlineKeyboardMarkup()
keyboard_axis_of_business_first.add(InlineKeyboardButton(text="Движение к цели", callback_data="first_flow_business_1"))
keyboard_axis_of_business_first.add(InlineKeyboardButton(text="Результативность", callback_data="first_flow_business_2"))
keyboard_axis_of_business_first.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="first_flow_business_3"))
keyboard_axis_of_business_first.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="first_flow_business_4"))
keyboard_axis_of_business_first.add(InlineKeyboardButton(text="Следующий", callback_data="first_flow_business_5"))

keyboard_axis_of_business_first_finish=InlineKeyboardMarkup()
keyboard_axis_of_business_first_finish.add(InlineKeyboardButton(text="Движение к цели", callback_data="first_flow_business_1"))
keyboard_axis_of_business_first_finish.add(InlineKeyboardButton(text="Результативность", callback_data="first_flow_business_2"))
keyboard_axis_of_business_first_finish.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="first_flow_business_3"))
keyboard_axis_of_business_first_finish.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="first_flow_business_4"))
keyboard_axis_of_business_first_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="first_flow_business_6"))

keyboard_axis_of_authority_first=InlineKeyboardMarkup()
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Развитие парадигмы децентрализации", callback_data="first_flow_authority_1"))
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Стратегическое развитие сообщества", callback_data="first_flow_authority_2"))
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Управление ресурсами", callback_data="first_flow_authority_3"))
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Управляемость проектов", callback_data="first_flow_authority_4"))
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Проф. доверие", callback_data="first_flow_authority_5"))
keyboard_axis_of_authority_first.add(InlineKeyboardButton(text="Следующий", callback_data="first_flow_authority_6"))

keyboard_axis_of_authority_first_finish=InlineKeyboardMarkup()
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Развитие парадигмы децентрализации", callback_data="first_flow_authority_1"))
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Стратегическое развитие сообщества", callback_data="first_flow_authority_2"))
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Управление ресурсами", callback_data="first_flow_authority_3"))
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Управляемость проектов", callback_data="first_flow_authority_4"))
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Проф. доверие", callback_data="first_flow_authority_5"))
keyboard_axis_of_authority_first_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="first_flow_authority_7"))
#----------

#-----Second flow-----
keyboard_axis_of_relations_second=InlineKeyboardMarkup()
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Честность", callback_data="second_flow_relations_1"))
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Ясность позиции", callback_data="second_flow_relations_2"))
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Уровень энергии", callback_data="second_flow_relations_3"))
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Устойчивость личностного роста", callback_data="second_flow_relations_4"))
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Интенсивность личностного роста", callback_data="second_flow_relations_5"))
keyboard_axis_of_relations_second.add(InlineKeyboardButton(text="Следующий", callback_data="second_flow_relations_6"))

keyboard_axis_of_relations_second_finish=InlineKeyboardMarkup()
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Честность", callback_data="second_flow_relations_1"))
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Ясность позиции", callback_data="second_flow_relations_2"))
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Уровень энергии", callback_data="second_flow_relations_3"))
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Устойчивость личностного роста", callback_data="second_flow_relations_4"))
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Интенсивность личностного роста", callback_data="second_flow_relations_5"))
keyboard_axis_of_relations_second_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="second_flow_relations_7"))

keyboard_axis_of_business_second=InlineKeyboardMarkup()
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Движение к цели", callback_data="second_flow_business_1"))
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Результативность", callback_data="second_flow_business_2"))
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="second_flow_business_3"))
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="second_flow_business_4"))
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="second_flow_business_5"))
keyboard_axis_of_business_second.add(InlineKeyboardButton(text="Следующий", callback_data="second_flow_business_6"))

keyboard_axis_of_business_second_finish=InlineKeyboardMarkup()
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Движение к цели", callback_data="second_flow_business_1"))
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Результативность", callback_data="second_flow_business_2"))
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="second_flow_business_3"))
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="second_flow_business_4"))
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="second_flow_business_5"))
keyboard_axis_of_business_second_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="second_flow_business_7"))

keyboard_axis_of_business_projects_second=InlineKeyboardMarkup()
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Движение к цели", callback_data="second_flow_projects__1"))
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Результативность", callback_data="second_flow_projects__2"))
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="second_flow_projects__3"))
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="second_flow_projects__4"))
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="second_flow_projects__5"))
keyboard_axis_of_business_projects_second.add(InlineKeyboardButton(text="Следующий", callback_data="second_flow_projects__6"))

keyboard_axis_of_business_projects_second_finish=InlineKeyboardMarkup()
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Движение к цели", callback_data="second_flow_projects__1"))
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Результативность", callback_data="second_flow_projects__2"))
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Адекватность картины мира", callback_data="second_flow_projects__3"))
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Ведение переговоров с внутренними и внешними референтными группами", callback_data="second_flow_projects__4"))
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Эффективность работы в команде", callback_data="second_flow_projects__5"))
keyboard_axis_of_business_projects_second_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="second_flow_projects__7"))

keyboard_axis_of_authority_second=InlineKeyboardMarkup()
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Развитие парадигмы децентрализации", callback_data="second_flow_authority_1"))
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Стратегическое развитие сообщества", callback_data="second_flow_authority_2"))
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Управление ресурсами", callback_data="second_flow_authority_3"))
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Управляемость проектов", callback_data="second_flow_authority_4"))
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Проф. доверие", callback_data="second_flow_authority_5"))
keyboard_axis_of_authority_second.add(InlineKeyboardButton(text="Следующий", callback_data="second_flow_authority_6"))

keyboard_axis_of_authority_second_finish=InlineKeyboardMarkup()
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Развитие парадигмы децентрализации", callback_data="second_flow_authority_1"))
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Стратегическое развитие сообщества", callback_data="second_flow_authority_2"))
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Управление ресурсами", callback_data="second_flow_authority_3"))
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Управляемость проектов", callback_data="second_flow_authority_4"))
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Проф. доверие", callback_data="second_flow_authority_5"))
keyboard_axis_of_authority_second_finish.add(InlineKeyboardButton(text="Завершить оценивание", callback_data="second_flow_authority_7"))

def ChooseKeyboardForFirstFlowRelations(nick,cursor):
    if(db_commands.GetCurrentFighterVoting(nick,cursor)==fighters_num-1):
        return keyboard_axis_of_relations_first_finish
    else:
        return keyboard_axis_of_relations_first

def ChooseKeyboardForFirstFlowBusiness():
    if (current_fighter_for_educator == fighters_num - 1):
        return keyboard_axis_of_business_first_finish
    else:
        return keyboard_axis_of_business_first

def ChooseKeyboardForFirstFlowAuthority():
    if (current_fighter_for_authority == fighters_num - 1):
        return keyboard_axis_of_authority_first_finish
    else:
        return keyboard_axis_of_authority_first

def ChooseKeyboardForSecondFlowRelations():
    if(current_fighter_for_tutor==second_flow_num-1):
        return keyboard_axis_of_relations_second_finish
    else:
        return keyboard_axis_of_relations_second

def ChooseKeyboardForSecondFlowBusiness():
    if (current_fighter_for_educator == second_flow_num - 1):
        return keyboard_axis_of_business_second_finish
    else:
        return keyboard_axis_of_business_second

def ChooseKeyboardForSecondFlowProjectBusiness():
    if (current_project_member == len(project_members) - 1):
        return keyboard_axis_of_business_projects_second_finish
    else:
        return keyboard_axis_of_business_projects_second

def ChooseKeyboardForSecondFlowAuthority():
    if (current_second_flow_for_authority == second_flow_num - 1):
        return keyboard_axis_of_authority_second_finish
    else:
        return keyboard_axis_of_authority_second
