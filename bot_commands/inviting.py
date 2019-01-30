# -*- coding: utf-8 -*-
from db_commands.db_users import *
from db_commands.db_profile import *
import telebot
from config import bot, db, cursor, get_keyboard, isRang

def add_abit(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [5, 7, 9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы абитуриентов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 8, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 8)
def adding_abit(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все абитуриенты успешно зачислены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            AddAbit(nick, cursor, db)
            bot.send_message(message.chat.id, "Абитуриент зачислен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


def add_investor(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы инвесторов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 811, cursor, db)


def add_tutor(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы тьюторов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 812, cursor, db)


def add_expert(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы экспертов, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 813, cursor, db)


def add_educator(message):
    if message.chat.type == 'private':
        if isRang(GetRangs('@' + message.from_user.username, cursor), [9]):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
            bot.send_message(message.chat.id,
                             'Введите никнеймы преподавателей, каждый отдельным сообщением. Для завершения нажмите на кнопку',
                             reply_markup=keyboard)
            username = "@" + message.from_user.username
            SetState(username, 814, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 811)
def adding_investor(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все инвесторы успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteInvestor(nick, cursor, db)
            bot.send_message(message.chat.id, "Инвестор добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 812)
def adding_tutor(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все тьюторы успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteTutor(nick, cursor, db)
            bot.send_message(message.chat.id, "Тьютор добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 813)
def adding_expert(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все эксперты успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteExpert(nick, cursor, db)
            bot.send_message(message.chat.id, "Эксперт добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)


@bot.message_handler(func=lambda message: GetState(message.from_user.username, cursor, db) == 814)
def adding_educator(message):
    nick = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.InlineKeyboardButton('Закончить'))
    if nick == 'Закончить':
        bot.send_message(message.chat.id, 'Все преподаватели успешно добавлены',
                         reply_markup=get_keyboard('@' + message.from_user.username))
        username = "@" + message.from_user.username
        SetState(username, 6, cursor, db)
    else:
        if nick[0] != '@':
            nick = "@" + nick
        if not (IsUserInDB(nick, cursor, db)):
            InviteEducator(nick, cursor, db)
            bot.send_message(message.chat.id, "Преподаватель добавлен", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Этот пользователь уже есть в базе", reply_markup=keyboard)