import datetime


# -*- coding: utf-8 -*-


def isRang(a, b):
    c = list(set(a) & set(b))
    return len(c) > 0


def AddAbit(nick, cursor, database):
    cursor.execute('INSERT INTO users(nickname,state, rangs) VALUES ("' + nick + '",0, "1|")')
    # AddRang(nick, 1, cursor, database)
    database.commit()


def IsAbit(nick, cursor, flag=False):
    if flag:
        rangs = GetInvitedRangs(nick, cursor)
    else:
        rangs = GetRangs(nick, cursor)
    return isRang(rangs, [1])


def IsInvitedInvestor(nick, cursor, flag=False):
    if flag:
        rangs = GetInvitedRangs(nick, cursor)
    else:
        rangs = GetRangs(nick, cursor)
    return isRang(rangs, [12])


def IsInvitedTutor(nick, cursor, flag=False):
    if flag:
        rangs = GetInvitedRangs(nick, cursor)
    else:
        rangs = GetRangs(nick, cursor)
    return isRang(rangs, [13])


def IsInvitedExpert(nick, cursor, flag=False):
    if flag:
        rangs = GetInvitedRangs(nick, cursor)
    else:
        rangs = GetRangs(nick, cursor)
    return isRang(rangs, [14])


def IsInvitedEducator(nick, cursor, flag=False):
    if flag:
        rangs = GetInvitedRangs(nick, cursor)
    else:
        rangs = GetRangs(nick, cursor)
    return isRang(rangs, [15])


def BecomeBeginner(id, cursor, database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(
        'UPDATE users SET authority=0.0,registration_date="' + now_date + '",sum_of_marks=0.0 WHERE id=' + str(id))

    #cursor.execute('INSERT INTO users_tokens(user_id,')
    database.commit()


def IsUserInDB(id, nickname, cursor):
    cursor.execute('SELECT * FROM users WHERE id=' + str(id))
    response1 = cursor.fetchall()
    cursor.execute('SELECT * FROM users WHERE nickname="' + nickname + '"')
    response2 = cursor.fetchall()
    return len(response1) > 0 or len(response2) > 0


def GetRangs(id, cursor):
    cursor.execute('SELECT rangs FROM users WHERE id=' + str(id))
    rangs = cursor.fetchall()[0][0]
    if rangs != None:
        rangs = rangs.split('|')
        int_rangs = list()
        for rang in rangs:
            try:
                int_rangs.append(int(rang))
            except:
                continue
        return int_rangs
    else:
        return []


def GetInvitedRangs(nickname, cursor):
    cursor.execute('SELECT rangs FROM users WHERE nickname="' + nickname + '"')
    rangs = cursor.fetchall()[0][0]
    if rangs != None:
        rangs = rangs.split('|')
        int_rangs = list()
        for rang in rangs:
            try:
                int_rangs.append(int(rang))
            except:
                continue
        return int_rangs
    else:
        return []


def listToRangs(rangs):
    rang_string = ''
    for rang in rangs:
        rang_string = rang_string + str(rang) + '|'
    return rang_string


def AddRang(id, rang, cursor, database):
    rangs = GetRangs(id, cursor)
    if not (rang in rangs):
        rangs.append(rang)
        rang_str = listToRangs(rangs)
        cursor.execute('UPDATE users SET rangs="' + rang_str + '" WHERE id=' + str(id))
        database.commit()


def DeleteRang(id, rang, cursor, database):
    rangs = GetRangs(id, cursor)
    rangs.remove(rang)
    rang_str = listToRangs(rangs)
    cursor.execute('UPDATE users SET rangs="' + rang_str + '" WHERE id=' + str(id))
    database.commit()


def GetListOfUsers(cursor):
    cursor.execute('SELECT id,name,chat_id FROM users where name is not null')
    return cursor.fetchall()


def InviteInvestor(nick, cursor, database):
    cursor.execute('INSERT INTO users(nickname,state, rangs) VALUES ("' + nick + '",0, "12|")')
    database.commit()


def InviteTutor(nick, cursor, database):
    cursor.execute('INSERT INTO users(nickname,state, rangs) VALUES ("' + nick + '",0, "13|")')
    database.commit()


def InviteExpert(nick, cursor, database):
    cursor.execute('INSERT INTO users(nickname,state, rangs) VALUES ("' + nick + '",0, "14|")')
    database.commit()


def InviteEducator(nick, cursor, database):
    cursor.execute('INSERT INTO users(nickname,state, rangs) VALUES ("' + nick + '",0, "15|")')
    database.commit()


def GetTitleOfRang(rang, cursor):
    cursor.execute('SELECT title FROM rangs WHERE id=' + str(rang))
    return cursor.fetchall()[0][0]


def GetInvestors(nick, cursor):
    cursor.execute('SELECT chat_id FROM users WHERE rang=8 AND nickname!="' + nick + '"')
    return cursor.fetchall()
