import datetime
from config import isRang
# -*- coding: utf-8 -*-

def AddAbit(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname,state) VALUES ("'+nick+'",0)')
    cursor.execute('INSERT INTO users_tokens(user,wallet,contribution_tokens,investment_tokens) VALUES ("'+nick+'","wallet",0.0, 0.0)')
    AddRang(nick, 1, cursor, database)
    database.commit()

def IsAbit(nick,cursor,database):
    rangs = GetRangs(nick, cursor)
    return isRang(rangs, [1])

def IsInvitedInvestor(nick,cursor,database):
    rangs = GetRangs(nick, cursor)
    return isRang(rangs, [12])

def IsInvitedTutor(nick,cursor,database):
    rangs = GetRangs(nick, cursor)
    return isRang(rangs, [13])

def IsInvitedExpert(nick,cursor,database):
    rangs = GetRangs(nick, cursor)
    return isRang(rangs, [14])

def IsInvitedEducator(nick,cursor,database):
    rangs = GetRangs(nick, cursor)
    return isRang(rangs, [15])

def BecomeBeginner(nick,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE users SET authority=0.0,balance=0.0,registration_date="'+now_date+'",sum_of_marks=0.0 WHERE nickname="'+nick+'"')
    database.commit()


def IsUserInDB(nick,cursor,database):
    cursor.execute('SELECT * FROM users WHERE nickname="'+nick+'"')
    response=cursor.fetchall()
    return len(response)>0

def GetRangs (nick,cursor):
    cursor.execute('SELECT rangs FROM users WHERE nickname="'+nick+'"')
    rangs = cursor.fetchall()[0][0]
    if rangs != None:
        rangs = rangs.split('|')
        int_rangs=list()
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

def AddRang(nick, rang, cursor, database):
        rangs = GetRangs(nick, cursor)
        if not (rang in rangs):
            rangs.append(rang)
            rang_str = listToRangs(rangs)
            cursor.execute('UPDATE users SET rangs="' + rang_str + '" WHERE nickname="' + nick + '"')
            database.commit()

def DeleteRang(nick, rang, cursor, database):
        rangs = GetRangs(nick, cursor)
        rangs.remove(rang)
        rang_str = listToRangs(rangs)
        cursor.execute('UPDATE users SET rangs="' + rang_str + '" WHERE nickname="' + nick + '"')
        database.commit()

def GetListOfUsers(cursor):
    cursor.execute('SELECT nickname,name,chat_id FROM users')
    return cursor.fetchall()

def InviteInvestor(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname) VALUES ("'+nick+'")')
    AddRang(nick, 12, cursor, database)
    database.commit()

def InviteTutor(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname) VALUES ("'+nick+'")')
    AddRang(nick, 13, cursor, database)
    database.commit()

def InviteExpert(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname) VALUES ("'+nick+'")')
    AddRang(nick, 14, cursor, database)
    database.commit()

def InviteEducator(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname) VALUES ("'+nick+'")')
    AddRang(nick, 15, cursor, database)
    database.commit()

def GetTitleOfRang(rang,cursor):
    cursor.execute('SELECT title FROM rangs WHERE id='+str(rang))
    return cursor.fetchall()[0][0]

def GetInvestors(nick,cursor):
    cursor.execute('SELECT chat_id FROM users WHERE rang=8 AND nickname!="'+nick+'"')
    return cursor.fetchall()