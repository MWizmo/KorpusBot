# -*- coding: utf-8 -*-


def GetMarks(nick,cursor):
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user="'+nick+'"')
    return cursor.fetchall()


def GetAllMarks(cursor):
    cursor.execute('SELECT sum_of_marks,nickname FROM users')
    return cursor.fetchall()


def GetAllExpertsMarksForDate(date, cursor):
    cursor.execute('SELECT expert,criterion,mark FROM expert_marks WHERE mark_date="'+date+'"')
    return cursor.fetchall()


def GetMarksForDate(date, axis, cursor):
    cursor.execute('SELECT user,criterion,mark FROM marks WHERE mark_date="' + date + '" AND axis=' + str(axis))
    return cursor.fetchall()


def GetMarksForDateAndUser(date, axis, user, cursor):
    cursor.execute('SELECT criterion,mark FROM marks WHERE mark_date="' + date + '" AND axis=' +
                   str(axis) + ' AND user="' + user + '"')
    return cursor.fetchall()


def GetAllDatesOfVotingByUser(user, cursor):
    cursor.execute('SELECT mark_date FROM marks WHERE user="' + user + '" GROUP BY mark_date')
    return cursor.fetchall()
