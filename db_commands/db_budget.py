# -*- coding: utf-8 -*-


def GetSumOfBudget(cursor):
    cursor.execute('SELECT budget FROM emission_data WHERE status="accepted"')
    return cursor.fetchone()[0]

def SetCoeff(coeff,cursor,database):
    cursor.execute('UPDATE emission_data SET tokens_per_human='+str(coeff)+' WHERE status="accepted"')
    database.commit()

def BudgetVote(num,cursor,database):
    if(num=='1'):
        cursor.execute('SELECT agree_number FROM voting WHERE status="active"')
        count=cursor.fetchall()[0][0]
        cursor.execute('UPDATE voting SET agree_number='+str(count+1)+' WHERE status="active"')
    else:
        cursor.execute('SELECT disagree_number FROM voting WHERE status="active"')
        count = cursor.fetchall()[0][0]
        cursor.execute('UPDATE voting SET disagree_number=' + str(count + 1)+' WHERE status="active"')
    database.commit()

def BudgetInfo(cursor):
    cursor.execute('SELECT agree_number,disagree_number,number_of_members FROM voting WHERE status="active"')
    arr=cursor.fetchall()[0]
    return 'За: '+str(arr[0])+'. Против: '+str(arr[1])+'. Число участников голосования: '+str(arr[2])


def CreateOrder(user,type,cursor,database):
    cursor.execute('INSERT INTO orders(user,type,status) VALUES ("'+user+'",'+str(type)+',"opened")')
    database.commit()
    cursor.execute('SELECT count(id) FROM orders')
    return cursor.fetchall()[0][0]

def CreatorOfOrder(order_id,cursor):
    cursor.execute('SELECT user FROM orders WHERE id='+str(order_id))
    return cursor.fetchall()[0][0]

def CloseOrder(order_id,cursor,database):
    cursor.execute('UPDATE orders SET status="closed" WHERE id='+str(order_id))
    database.commit()