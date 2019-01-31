# -*- coding: utf-8 -*-


def GetMarks(nick,cursor):
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user="'+nick+'"')
    return cursor.fetchall()


def GetAllMarks(cursor):
    cursor.execute('SELECT sum_of_marks,nickname FROM users')
    return cursor.fetchall()