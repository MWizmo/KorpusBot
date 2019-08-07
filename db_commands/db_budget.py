# -*- coding: utf-8 -*-
import datetime


def GetSumOfBudget(cursor):
    cursor.execute('SELECT budget FROM emission_data WHERE status="accepted"')
    return cursor.fetchone()[0]


def SetCoeff(coeff, cursor, database):
    cursor.execute('UPDATE emission_data SET tokens_per_human=' + str(coeff) + ' WHERE status="accepted"')
    database.commit()


def BudgetVote(num, authority, cursor, database):
    if authority == 0:
        authority = 1
    if num == '1':
        cursor.execute('SELECT agree_number FROM budget_votings WHERE status="active"')
        count = cursor.fetchall()[0][0]
        cursor.execute('UPDATE budget_votings SET agree_number=' + str(count + authority) + ' WHERE status="active"')
    else:
        cursor.execute('SELECT disagree_number FROM budget_votings WHERE status="active"')
        count = cursor.fetchall()[0][0]
        cursor.execute('UPDATE budget_votings SET disagree_number=' + str(count + authority) + ' WHERE status="active"')
    database.commit()


def BudgetInfo(cursor, is_end=False):
    status = '"active"'
    if is_end:
        status = '"finished" order by id desc'
    cursor.execute('SELECT agree_number,disagree_number,number_of_members FROM budget_votings WHERE status=' + status)
    arr = cursor.fetchall()[0]
    return 'За: ' + str(arr[0]) + '. Против: ' + str(arr[1]) + '. Число участников голосования: ' + str(arr[2])


def CreateOrder(user, type, cursor, database):
    cursor.execute('INSERT INTO orders(user,type,status) VALUES ("' + user + '",' + str(type) + ',"opened")')
    database.commit()
    cursor.execute('SELECT count(id) FROM orders')
    return cursor.fetchall()[0][0]


def CreatorOfOrder(order_id, cursor):
    cursor.execute('SELECT user FROM orders WHERE id=' + str(order_id))
    return cursor.fetchall()[0][0]


def CloseOrder(order_id, cursor, database):
    cursor.execute('UPDATE orders SET status="closed" WHERE id=' + str(order_id))
    database.commit()


def IsThereActiveVoting(cursor):
    cursor.execute('SELECT * FROM budget_votings WHERE status="active"')
    return len(cursor.fetchall()) > 0


def StartVoting(chat_id, user, number, summa, cursor, database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(
        'INSERT INTO budget_votings(chat_id,creator_id,number_of_members,agree_number,disagree_number,start_date,status) values ("' + str(
            chat_id) + '",' + str(user) + ',' + str(number) +
        ',0,0,"' + now_date + '","active")')
    cursor.execute('UPDATE emission_data SET status="not actual" WHERE status="accepted"')
    cursor.execute('INSERT INTO emission_data(budget,status) VALUES (' + str(summa) + ',"voting")')
    database.commit()


def GetUserWhoStartedVoting(cursor):
    cursor.execute('SELECT creator_id FROM budget_votings WHERE status="active"')
    return cursor.fetchall()[0][0]


def FinishVoting(cursor, database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE budget_votings SET finish_date="' + now_date + '" WHERE status="active"')
    cursor.execute('UPDATE budget_votings SET status="finished" WHERE status="active"')
    cursor.execute('UPDATE emission_data SET status="accepted" WHERE status="voting"')
    database.commit()
