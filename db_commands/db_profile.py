# -*- coding: utf-8 -*-


def SetChatId(id, chat_id, cursor, database):
    cursor.execute('UPDATE users SET chat_id=' + str(chat_id) + ' WHERE id=' + str(id))
    database.commit()


def SetId(nick, id, cursor, db):
    cursor.execute('UPDATE users SET id=' + str(id) + ' WHERE nickname="'+nick+'"')
    db.commit()


def GetChatId(id, cursor):
    cursor.execute('SELECT chat_id FROM users WHERE id=' + str(id))
    return cursor.fetchall()[0][0]


def GetAuthority(id, cursor):
    cursor.execute('SELECT authority FROM users WHERE id=' + str(id))
    return cursor.fetchall()[0][0]


def GetName(id, cursor):
    cursor.execute('SELECT name FROM users WHERE id=' + str(id))
    name = cursor.fetchone()[0]
    return name


def UpdateExrtaInfo(id, extra_info, cursor, database):
    cursor.execute('UPDATE users SET extra_info="' + extra_info + '" WHERE id=' + str(id))
    database.commit()


def UpdateName(id, name, cursor, database):
    cursor.execute('UPDATE users SET name="' + name + '" WHERE id=' + str(id))
    database.commit()


def UpdatePhone(id, phone, cursor, database):
    cursor.execute('UPDATE users SET phone="' + str(phone) + '" WHERE id=' + str(id))
    database.commit()

def UpdateEmail(id, email, cursor, database):
    cursor.execute('UPDATE users SET email="' + email + '" WHERE id=' + str(id))
    database.commit()

def UpdatePhoto(id, photo, cursor, database):
    cursor.execute('UPDATE users SET photo="' + photo + '" WHERE id=' + str(id))
    database.commit()


def UpdateWallet(id, wallet, cursor, database):
    cursor.execute('SELECT * from users_tokens where user_id='+str(id))
    if len(cursor.fetchall()):
        cursor.execute('UPDATE users_tokens SET wallet="' + wallet + '" WHERE user_id=' + str(id))
    else:
        cursor.execute(
            'INSERT INTO users_tokens(user_id,wallet,contribution_tokens,investment_tokens) VALUES (' + str(
                id) + ',"wallet",0.0, 0.0)')
    database.commit()


def GetWallet(id, cursor):
    cursor.execute('SELECT wallet FROM users_tokens WHERE user_id=' + str(id))
    return cursor.fetchone()[0]


def SetDossier(dossier, id, cursor, database):
    cursor.execute('UPDATE users SET dossier="' + dossier + '" WHERE id=' + str(id))
    database.commit()


def GetDossier(id, cursor):
    cursor.execute('SELECT dossier FROM users WHERE id =' + str(id))
    a = cursor.fetchone()[0]
    return a


def UpdateProfile(id, name, photo_url, phone, email, cursor, database):
    cursor.execute('UPDATE users SET name="' + name + '", photo="' + photo_url + '",phone="' + str(
        phone) + '",email="' + email + '" WHERE id=' + str(id))
    database.commit()


def SetState(id, state, cursor, database):
    cursor.execute('UPDATE users SET state="' + str(state) + '" WHERE id=' + str(id))
    database.commit()


def GetState(id, cursor):
    cursor.execute('SELECT state FROM users WHERE id=' + str(id))
    state = cursor.fetchone()
    if state is None:
        return -1
    else:
        return state[0]


def GetProfile(id, cursor):
    cursor.execute(
        'SELECT name,phone,email,photo,authority,registration_date,sum_of_marks,dossier FROM users WHERE id=' + str(id))
    return cursor.fetchall()[0]
