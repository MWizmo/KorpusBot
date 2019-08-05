# -*- coding: utf-8 -*-
from db_commands.db_profile import *
from db_commands.db_users import *
from db_commands.db_tokens import GetInvestmentTokens, GetContributionTokens
from db_commands.db_projects import GetProjectsOfUser
import re
import telebot
import config
from config import bot, db, cursor, get_keyboard, isRang


def reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Введите свое полное имя")
    SetState(message.from_user.id, 1, cursor, db)


def red_profile(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text='Имя', callback_data='profile_1'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Телефон', callback_data='profile_2'))
    keyboard.add(
        telebot.types.InlineKeyboardButton(text='Электронный адрес Google-аккаунта', callback_data='profile_3'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Фото', callback_data='profile_4'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Адрес Etherium-кошелька', callback_data='profile_6'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Закончить', callback_data='profile_5'))
    bot.send_message(message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('profile'))
def redacting_profile(call):
    if call.data[-1] == '1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новое имя')
        SetState(call.from_user.id, 41, cursor, db)
    elif call.data[-1] == '2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый телефон')
        SetState(call.from_user.id, 42, cursor, db)
    elif call.data[-1] == '3':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый электронный адрес Google-аккаунта')
        SetState(call.from_user.id, 43, cursor, db)
    elif call.data[-1] == '4':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Загрузите новое фото')
        SetState(call.from_user.id, 44, cursor, db)
    elif call.data[-1] == '6':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Введите новый адрес кошелька')
        SetState(call.from_user.id, 45, cursor, db)
    elif call.data[-1] == '5':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Редактирование окончено',
                         reply_markup=get_keyboard(call.from_user.id))
        SetState(call.from_user.id, 6, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 41)
def user_redacting_fio(message):
    name = message.text
    UpdateName(message.from_user.id, name, cursor, db)
    bot.send_message(message.chat.id, text='Имя изменено')
    SetState(message.from_user.id, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 42)
def user_redacting_phone(message):
    phone = message.text
    if re.fullmatch(r'\+7\d{10}', phone) or re.fullmatch(r'8\d{10}', phone):
        UpdatePhone(message.from_user.id, phone, cursor, db)
        bot.send_message(message.chat.id, text='Телефон изменен')
        SetState(message.from_user.id, 6, cursor, db)
        red_profile(message)
    else:
        bot.send_message(message.chat.id, 'Введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX')


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 43)
def user_redacting_email(message):
    email = message.text
    if re.fullmatch(r'\w+@[a-z]+\.[a-z]{,4}', email):
        UpdateEmail(message.from_user.id, email, cursor, db)
        bot.send_message(message.chat.id, text='Электронный адрес изменен')
        SetState(message.from_user.id, 6, cursor, db)
        red_profile(message)
    else:
        bot.send_message(message.chat.id, 'Введите адрес электронной почты в формате *@*.*')


@bot.message_handler(content_types=["photo"],
                     func=lambda message: GetState(message.from_user.id, cursor) == 44)
def user_redacting_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    UpdatePhoto(message.from_user.id, photo, cursor, db)
    bot.send_message(message.chat.id, text='Фото изменено')
    SetState(message.from_user.id, 6, cursor, db)
    red_profile(message)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 45)
def user_redacting_wallet(message):
    wallet = message.text
    UpdateWallet(message.from_user.id, wallet, cursor, db)
    bot.send_message(message.chat.id, text='Адрес кошелька изменен')
    SetState(message.from_user.id, 6, cursor, db)
    red_profile(message)


def get_profile(message):
    if message.chat.type == 'private':
        if isRang(GetRangs(message.from_user.id, cursor), [2, 3, 4, 5, 6, 7, 8, 9, 10]):
            profile = GetProfile(message.from_user.id, cursor)
            if profile[0] != None:
                string = 'Пользователь: ' + profile[0]
                string += "\nФото: "
                bot.send_message(message.chat.id, string)
                try:
                    bot.send_photo(message.chat.id, profile[3])
                except telebot.apihelper.ApiException:
                    bot.send_message(message.chat.id, 'Фото недоступно')
                try:
                    string = "Телефон: " + str(profile[1])
                except:
                    pass
                try:
                    string = string + "\nGoogle-аккаунт: " + profile[2]
                except:
                    pass
                try:
                    string = string + "\nДата регистрации: " + profile[5]
                    string = string + '\nАвторитет: ' + str(profile[4])
                    if profile[6] == None:
                        string = string + '\nСумма оценок в текущем месяце: 0'
                    else:
                        string = string + '\nСумма оценок в текущем месяце: ' + str(profile[6])
                    if profile[7] != None:
                        string = string + '\nДосье: ' + profile[7]
                    wallet = GetWallet(message.from_user.id, cursor)
                    if wallet != 'wallet':
                        string = string + '\nEtherium-кошелек:' + wallet
                    try:
                        string = string + '\nТокены вклада: ' + str(
                            GetContributionTokens(message.from_user.id, cursor))
                        string = string + '\nТокены инвестиций: ' + str(
                            GetInvestmentTokens(message.from_user.id, cursor))
                    except:
                        print("Fix it 2")
                except:
                    print("Fix it")
                string = string + '\nРоли в системе: '
                rangs = GetRangs(message.from_user.id, cursor)
                for rang in rangs:
                    string = string + GetTitleOfRang(rang, cursor) + ', '
                string = string[:len(string) - 2]
                projects = GetProjectsOfUser(message.from_user.id, cursor)
                if len(projects):
                    string += '\nСостоит в проектах: '
                    for project in projects:
                        string += '"' + project[0] + '", '
                    string = string[:len(string) - 2]
                else:
                    string += '\nАктивных проектов нет'
                bot.send_message(message.chat.id, string,
                                 reply_markup=get_keyboard(message.from_user.id))
            else:
                bot.send_message(message.chat.id, "Ой, анкета еще не заполнена",
                                 reply_markup=get_keyboard(message.from_user.id))
            SetState(message.from_user.id, 6, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 1)
def user_entering_fio(message):
    if IsAbit(message.from_user.id, cursor):
        name = message.text
        bot.send_message(message.chat.id, "Всё, кажется запомнил. Теперь напиши свой номер телефона, он мне пригодится")
        SetState(message.from_user.id, 2, cursor, db)
    elif IsInvitedExpert(message.from_user.id, cursor):
        name = message.text
        bot.send_message(message.chat.id,
                         "Напишите, пожалуйста, в какиx областяx вы являетесь экспертом")
        SetState(message.from_user.id, 101, cursor, db)
    else:
        name = message.text
        bot.send_message(message.chat.id,
                         "Отлично. Для контакта с вами нам может потребоваться номер вашего мобильного телефона. Введите его, пожалуйста")
        SetState(message.from_user.id, 2, cursor, db)
    UpdateName(message.from_user.id, name, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 101)
def user_entering_expertness(message):
    expertness = message.text
    UpdateExrtaInfo(message.from_user.id, expertness, cursor, db)
    bot.send_message(message.chat.id,
                     "Отлично. Для контакта с вами нам может потребоваться номер вашего мобильного телефона. Введите его, пожалуйста")
    SetState(message.from_user.id, 2, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 2)
def user_entering_phone(message):
    phone = message.text
    if re.fullmatch(r'\+7\d{10}', phone) or re.fullmatch(r'8\d{10}', phone):
        if IsAbit(message.from_user.id, cursor):
            bot.send_message(message.chat.id, "Номер есть, тепeрь дай мне адрес своего Google-аккаунта")
            SetState(message.from_user.id, 3, cursor, db)
        else:
            bot.send_message(message.chat.id, "Также нам может потребоваться ваш Google-аккаунт. Введите и его.")
            SetState(message.from_user.id, 3, cursor, db)
        UpdatePhone(message.from_user.id, phone, cursor, db)
    else:
        bot.send_message(message.chat.id, 'Введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX')


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 3)
def user_entering_email(message):
    email = message.text
    pattern = r"^[a-zA-Z0-9]{1,100}[@][a-z]{2,16}\.[a-z]{2,4}"
    email_re = re.compile(pattern)
    if email_re.findall(email):
        # if re.match(r'@', email):
        if IsAbit(message.from_user.id, cursor):
            bot.send_message(message.chat.id,
                             "Для полноценной работы в системе нужен Etherium-кошелек. Введи его адрес")
            SetState(message.from_user.id, 5, cursor, db)
        else:
            bot.send_message(message.chat.id,
                             "Для полноценной работы в системе нужен Etherium-кошелек. Введите его адрес")
            SetState(message.from_user.id, 5, cursor, db)
        UpdateEmail(message.from_user.id, email, cursor, db)
    else:
        bot.send_message(message.chat.id, 'Введите адрес электронной почты в формате *@*.*')


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 5)
def user_entering_wallet(message):
    if IsAbit(message.from_user.id, cursor):
        wallet = message.text
        bot.send_message(message.chat.id, "Принял, теперь мне нужна твоя фотография, только давай без приколов")
        SetState(message.from_user.id, 4, cursor, db)
    else:
        wallet = message.text
        bot.send_message(message.chat.id,
                         "Для упрощения нашего взаимодействия через систему загрузите, пожалуйста, свою фотографию.")
        SetState(message.from_user.id, 4, cursor, db)
    UpdateWallet(message.from_user.id, wallet, cursor, db)


@bot.message_handler(content_types=["photo"],
                     func=lambda message: GetState(message.from_user.id, cursor) == 4)
def user_entering_pic(message):
    photo = message.photo[len(message.photo) - 1].file_id
    id = message.from_user.id
    if IsAbit(id, cursor):
        DeleteRang(id, 1, cursor, db)
        AddRang(id, 2, cursor, db)
        bot.send_message(message.chat.id, "Красавчик, спасибо. Отныне ты курсант антишколы Корпус!",
                         reply_markup=get_keyboard(message.from_user.id))
    elif IsInvitedInvestor(id, cursor):
        DeleteRang(id, 12, cursor, db)
        AddRang(id, 8, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard(message.from_user.id))
    elif IsInvitedTutor(id, cursor):
        DeleteRang(id, 13, cursor, db)
        AddRang(id, 5, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard(message.from_user.id))
    elif IsInvitedEducator(id, cursor):
        DeleteRang(id, 15, cursor, db)
        AddRang(id, 6, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard(message.from_user.id))
    elif IsInvitedExpert(id, cursor):
        DeleteRang(id, 14, cursor, db)
        AddRang(id, 10, cursor, db)
        bot.send_message(message.chat.id, "Cпасибо. Теперь вы полноправный член нашей системы!",
                         reply_markup=get_keyboard(message.from_user.id))
    else:
        # UpdateProfile(username, user_info['name'], photo, user_info['phone'], user_info['email'], cursor, db)
        bot.send_message(message.chat.id, "Профиль обновлен",
                         reply_markup=get_keyboard(message.from_user.id))
    UpdatePhoto(id, photo, cursor, db)
    BecomeBeginner(id, cursor, db)
    SetChatId(id, message.chat.id, cursor, db)
    SetState(id, 6, cursor, db)


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 4)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 44)
def user_entered_not_pic(message):
    bot.send_message(message.chat.id, "Необходимо загрузить изображение")


@bot.message_handler(commands=["id"])
def get_id(message):
    if message.chat.type == 'private':
        try:
            SetId('@' + message.from_user.id, message.from_user.id, cursor, db)
            SetChatId(message.from_user.id, message.chat.id, cursor, db)
        finally:
            bot.send_message(message.chat.id, 'Ok',
                         reply_markup=get_keyboard(message.from_user.id))


def look_profiles(message):
    if message.chat.type == 'private': #and isRang(GetRangs(message.from_user.id, cursor), [5, 8, 9, 10]):
        students = GetListOfUsers(cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for student in students:
            name = student[1]
            if name == None:
                name = student[0]
            keyboard.add(telebot.types.InlineKeyboardButton(text=name, callback_data='look_profile_of_' + str(student[0])))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text='<Вернуться в главное меню>', callback_data='look_profile_of_*'))
        bot.send_message(message.chat.id, 'Выберите пользователя', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_profile_of'))
def looking_profile(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data[-1] == '*':
        bot.send_message(call.message.chat.id, 'Главное меню',
                         reply_markup=get_keyboard(call.from_user.id))
    else:
        profile = GetProfile(call.data[16:], cursor)
        if profile[0] != None:
            string = 'Пользователь: ' + profile[0]
            string += "\nФото: "
            bot.send_message(call.message.chat.id, string)
            if profile[3] != None:
                bot.send_photo(call.message.chat.id, profile[3])
            else:
                bot.send_message(call.message.chat.id, 'Фото недоступно')
            string = "Телефон: " + str(profile[1])
            string = string + "\nЭлектронная почта: " + profile[2]
            string = string + "\nДата регистрации: " + profile[5]
            string = string + '\nАвторитет: ' + str(profile[4])
            if profile[6] != None:
                    string = string + '\nСумма оценок в текущем месяце: ' + str(profile[6])
            if profile[7] != None:
                    string = string + '\nДосье: ' + profile[8]
            wallet = GetWallet(call.data[16:], cursor)
            if wallet != 'wallet':
                    string = string + '\nEtherium-кошелек:' + wallet
            try:
                string = string + '\nТокены вклада: ' + str(
                    GetContributionTokens(call.data[16:], cursor))
                string = string + '\nТокены инвестиций: ' + str(
                    GetInvestmentTokens(call.data[16:], cursor))
            except:
                    print("Fix it 2")
            string = string + '\nРоли в системе: '
            rangs = GetRangs(call.data[16:], cursor)
            for rang in rangs:
                    string = string + GetTitleOfRang(rang, cursor) + ', '
            string = string[:len(string) - 2]
            projects = GetProjectsOfUser(call.data[16:], cursor)
            if len(projects):
                string += '\nСостоит в проектах: '
                for project in projects:
                    string += '"' + project[0] + '", '
                string = string[:len(string) - 2]
            else:
                string += '\nАктивных проектов нет'
            bot.send_message(call.message.chat.id, string,
                                 reply_markup=get_keyboard(call.from_user.id))
            # except:
            #     bot.send_message(call.message.chat.id, "Анкета заполнена не полностью",
            #                      reply_markup=get_keyboard(call.from_user.id))
        else:
            bot.send_message(call.message.chat.id, "Ой, анкета еще не заполнена",
                             reply_markup=get_keyboard(call.from_user.id))


def set_rang(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0], cursor), callback_data='csr%' + str(user[0])))
    keyboard.add(telebot.types.InlineKeyboardButton(text='<Назад>', callback_data='csr%back'))
    bot.send_message(message.chat.id, 'Чей ранг вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('csr'))
def setting_rang1(call):
    if call.data.split('%')[1] == 'back':
        SetState(call.from_user.id, 6, cursor, db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Главное меню",
                         reply_markup=get_keyboard(call.from_user.id))
    else:
        nick = call.data.split('%')[1]
        rangs = GetRangs(nick, cursor)
        str_rang = ''
        for rang in rangs:
            str_rang = str_rang + GetTitleOfRang(rang, cursor) + ', '
        str_rang = str_rang[:len(str_rang) - 2]
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Первый курс', callback_data='set_rang_2#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Второй курс', callback_data='set_rang_3#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Третий курс', callback_data='set_rang_4#' + str(nick)))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Тьютор', callback_data='set_rang_5#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Преподаватель', callback_data='set_rang_6#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Head teacher', callback_data='set_rang_11#' + str(nick)))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Трекер', callback_data='set_rang_7#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Эксперт', callback_data='set_rang_10#' + str(nick)))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Инвестор', callback_data='set_rang_8#' + str(nick)),
                     telebot.types.InlineKeyboardButton(text='Admin', callback_data='set_rang_9#' + str(nick)))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Выберите роль для пользователя ' + GetName(nick,
                                                                     cursor) + ' (текущие роли: ' + str_rang + ')',
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('set_rang'))
def setting_rang2(call):
    text = call.data[9:]
    words = text.split('#')
    rang = int(words[0])
    nick = words[1]
    AddRang(nick, rang, cursor, db)
    SetState(nick, 6, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Успешно",
                     reply_markup=get_keyboard(call.from_user.id))
    bot.send_message(GetChatId(nick, cursor), 'Вам добавлена роль "'+GetTitleOfRang(rang, cursor)+'"')


def delete_rang(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        keyboard.add(telebot.types.InlineKeyboardButton(text=GetName(user[0], cursor), callback_data='cdr%' + str(user[0])))
    keyboard.add(telebot.types.InlineKeyboardButton(text='<Назад>', callback_data='cdr%back'))
    bot.send_message(message.chat.id, 'Чей ранг вы хотите изменить?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('cdr'))
def deleting_rang1(call):
    nick = call.data.split('%')[1]
    if nick == 'back':
        SetState(call.from_user.id, 6, cursor, db)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Главное меню",
                         reply_markup=get_keyboard(call.from_user.id))
    else:
        rangs = GetRangs(nick, cursor)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for rang in rangs:
            keyboard.add(telebot.types.InlineKeyboardButton(text=GetTitleOfRang(rang, cursor),
                                                            callback_data='del_rang%' + str(rang) + '%' + str(nick)))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         'Выберите роль, которую вы хотите убрать у пользователя ' + GetName(nick, cursor),
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('del_rang'))
def deleting_rang2(call):
    words = call.data.split('%')
    rang = words[1]
    nick = words[2]
    DeleteRang(nick, int(rang), cursor, db)
    SetState(nick, 6, cursor, db)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Успешно",
                     reply_markup=get_keyboard(call.from_user.id))
    bot.send_message(GetChatId(nick, cursor), 'У вас убрали роль "' + GetTitleOfRang(rang, cursor) + '"')


def add_dosier(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
            name = user[1]
            if name == None:
                name = user[0]
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=name, callback_data='add_dosier%' + str(user[0])))
    bot.send_message(message.chat.id, 'Кому вы хотите добавить или изменить досье?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('add_dosier'))
def setting_dosier1(call):
    nick = call.data.split('%')[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,
                     'Вставьте ссылку на документ с досье курсанта или отправьте его в виде сообщения')
    SetState(call.from_user.id, 61, cursor, db)
    config.current_user_for_dossier = nick


@bot.message_handler(func=lambda message: GetState(message.from_user.id, cursor) == 61)
def setting_dosier2(message):
    dossier = message.text
    SetDossier(dossier, config.current_user_for_dossier, cursor, db)
    SetState(message.from_user.id, 6, cursor, db)
    bot.send_message(message.chat.id, "Успешно",
                     reply_markup=get_keyboard(message.from_user.id))


def look_dosier(message):
    users = GetListOfUsers(cursor)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for user in users:
        if isRang(GetRangs(user[0], cursor), [2, 3, 4]):
            name = user[1]
            if name == None:
                name = user[0]
            keyboard.add(
                telebot.types.InlineKeyboardButton(text=name, callback_data='look_dosier%' + str(user[0])))
    bot.send_message(message.chat.id, 'Чьё досье вы хотите посмотреть?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True and call.data.startswith('look_dosier'))
def looking_dosier(call):
    nick = call.data.split('%')[1]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    dossier = GetDossier(nick, cursor)
    if dossier == -1:
        bot.send_message(call.message.chat.id, 'Досье для данного пользователя еще не добавлено',
                         reply_markup=get_keyboard(call.from_user.id))
    else:
        bot.send_message(call.message.chat.id, 'Досье пользователя ' + nick + ':\n\n' + dossier,
                         reply_markup=get_keyboard(call.from_user.id))
