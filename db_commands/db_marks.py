# -*- coding: utf-8 -*-


def GetMarks(user_id,cursor):
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user_id='+str(user_id))
    return cursor.fetchall()


def GetAllMarks(cursor):
    cursor.execute('SELECT sum_of_marks,id FROM users')
    return cursor.fetchall()


def GetAllExpertsMarksForDate(date, cursor):
    cursor.execute('SELECT expert_id,criterion,mark FROM expert_marks WHERE mark_date="'+date+'"')
    return cursor.fetchall()


def GetMarksForDate(date, axis, cursor):
    cursor.execute('SELECT user_id,criterion,mark FROM marks WHERE mark_date="' + date + '" AND axis=' + str(axis))
    return cursor.fetchall()


def GetMarksForDateAndUser(date, axis, user_id, cursor):
    cursor.execute('SELECT criterion,mark FROM marks WHERE mark_date="' + date + '" AND axis=' +
                   str(axis) + ' AND user_id=' + str(user_id))
    return cursor.fetchall()


def GetAllDatesOfVotingByUser(user_id, cursor):
    cursor.execute('SELECT mark_date FROM marks WHERE user_id=' + str(user_id) + ' GROUP BY mark_date')
    return cursor.fetchall()


def GetAllMarksForDate(user_id, date, cursor):
    cursor.execute('SELECT mark FROM marks where user_id=' + str(user_id) + ' AND mark_date="' + date + '"')
    return cursor.fetchall()


def AddMarksToUser(user_id, time, cursor, db):
    cursor.execute('SELECT mark FROM marks where user_id=' + str(user_id) + ' AND mark_date="' + time + '"')
    marks = cursor.fetchall()
    cursor.execute('SELECT sum_of_marks FROM users WHERE id=' + str(user_id))
    summa = float(cursor.fetchone()[0])
    for mark in marks:
        summa += float(mark[0])
    cursor.execute('UPDATE users SET sum_of_marks = ' + str(summa) +' WHERE id=' + str(user_id))
    db.commit()
