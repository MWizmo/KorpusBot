# -*- coding: utf-8 -*-


def SetChatId(nick,chat_id,cursor,database):
    cursor.execute('UPDATE users SET chat_id='+str(chat_id)+' WHERE nickname="'+nick+'"')
    database.commit()

def GetChatId(nick,cursor):
    cursor.execute('SELECT chat_id FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchall()[0][0]

def GetAuthority(user,cursor):
    cursor.execute('SELECT authority FROM users WHERE nickname="'+user+'"')
    return cursor.fetchall()[0][0]

def GetName(nick,cursor):
    cursor.execute('SELECT name FROM users WHERE nickname="' + nick + '"')
    name = cursor.fetchone()[0]
    if name == None:
        return nick
    else:
        return name

def UpdateExrtaInfo(nick,extra_info,cursor,database):
    cursor.execute('UPDATE users SET extra_info="' + extra_info + '" WHERE nickname="' + nick + '"')
    database.commit()

def UpdateName(nick,name,cursor,database):
    cursor.execute('UPDATE users SET name="'+name+'" WHERE nickname="'+nick+'"')
    database.commit()

def UpdatePhone(nick,phone,cursor,database):
    cursor.execute('UPDATE users SET phone="'+str(phone)+'" WHERE nickname="'+nick+'"')
    database.commit()

def UpdateEmail(nick,email,cursor,database):
    cursor.execute('UPDATE users SET email="'+email+'" WHERE nickname="'+nick+'"')
    database.commit()

def UpdatePhoto(nick,photo,cursor,database):
    cursor.execute('UPDATE users SET photo="'+photo+'" WHERE nickname="'+nick+'"')
    database.commit()

def UpdateWallet(nick, wallet, cursor, database):
    cursor.execute('UPDATE users_tokens SET wallet="' + wallet + '" WHERE user="' + nick + '"')
    database.commit()

def GetWallet(nick, cursor):
    cursor.execute('SELECT wallet FROM users_tokens WHERE user="' + nick + '"')
    return cursor.fetchone()[0]

def SetDossier(dossier,nick,cursor,database):
    cursor.execute('UPDATE users SET dossier="'+dossier+'" WHERE nickname="'+nick+'"')
    database.commit()

def GetDossier(nick,cursor):
    cursor.execute('SELECT dossier FROM users WHERE nickname ="'+nick+'"')
    a=cursor.fetchone()[0]
    return a

def UpdateProfile(nick,name,photo_url,phone,email,cursor,database):
    cursor.execute('UPDATE users SET name="' + name + '", photo="' + photo_url + '",phone="' + str(
        phone) + '",email="' + email + '" WHERE nickname="' + nick + '"')
    database.commit()

def SetState (nick,state,cursor,database):
    cursor.execute('UPDATE users SET state="'+str(state)+'" WHERE nickname="'+nick+'"')
    database.commit()

def GetState (nick,cursor,database):
    if(nick[0]!='@'):
        nick="@"+nick
    cursor.execute('SELECT state FROM users WHERE nickname="'+nick+'"')
    state=cursor.fetchone()
    if state!=None:
        return state[0]
    else:
        return -1

def GetProfile(nick,cursor):
    if (nick[0] != '@'):
        nick = "@" + nick
    cursor.execute('SELECT name,phone,email,photo,authority,registration_date,sum_of_marks,dossier FROM users WHERE nickname="' + nick + '"')
    return cursor.fetchall()[0]

