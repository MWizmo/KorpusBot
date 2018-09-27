# -*- coding: utf-8 -*-
import sqlite3
import datetime

def AddAbit(nick,cursor,database):
    cursor.execute('INSERT INTO users(rang,nickname,state) VALUES (1,"'+nick+'",0)')
    database.commit()

def IsAbit(nick,cursor,database):
    cursor.execute('SELECT * FROM users WHERE nickname="'+nick+'" AND rang=1')
    response=cursor.fetchall()
    return len(response)>0

def IsInvitedInvestor(nick,cursor,database):
    cursor.execute('SELECT * FROM users WHERE nickname="'+nick+'" AND rang=12')
    response=cursor.fetchall()
    return len(response)>0

def BecomeInvestor(nick,name,photo_url,phone,email,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE users SET name="' + name + '", photo="' + photo_url + '",phone="' + str(
        phone) + '",email="' + email + '",rang=8,balance=0.0,authority=0.0,registration_date="' + now_date + '" WHERE nickname="' + nick + '"')
    database.commit()

def IsUserInDB(nick,cursor,database):
    cursor.execute('SELECT * FROM users WHERE nickname="'+nick+'"')
    response=cursor.fetchall()
    return len(response)>0

def UpgradeTo1(nick,name,photo_url,phone,email,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE users SET name="'+name+'", photo="'+photo_url+'",phone="'+str(phone)+'",email="'+email+'",rang=2,balance=0.0,authority=0.0,registration_date="'+now_date+'" WHERE nickname="'+nick+'"')
    database.commit()

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
    state=cursor.fetchall()[0][0]
    if state!=None:
        return state
    else:
        return -1

def SetRang (nick,rang,cursor,database):
    cursor.execute('UPDATE users SET rang="'+str(rang)+'" WHERE nickname="'+nick+'"')
    database.commit()

def SetSecondRang (nick,rang,cursor,database):
    cursor.execute('UPDATE users SET second_rang="'+str(rang)+'" WHERE nickname="'+nick+'"')
    database.commit()

def GetRang (nick,cursor):
    if (nick[0] != '@'):
        nick = "@" + nick
    cursor.execute('SELECT rang FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchall()[0][0]

def GetSecondRang (nick,cursor):
    if (nick[0] != '@'):
        nick = "@" + nick
    cursor.execute('SELECT second_rang FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchall()[0][0]

def GetProfile(nick,cursor):
    if (nick[0] != '@'):
        nick = "@" + nick
    cursor.execute('SELECT name,phone,email,photo,authority,balance,registration_date,sum_of_marks,dossier FROM users WHERE nickname="' + nick + '"')
    return cursor.fetchall()[0]

def GetListOfUsers(cursor):
    cursor.execute('SELECT nickname,rang,second_rang,chat_id,sum_of_marks,name FROM users')
    return cursor.fetchall()

def GetListOfStudents(cursor):
    cursor.execute('SELECT name,nickname,rang,second_rang,email,phone,photo,sum_of_marks,authority FROM users WHERE rang=2 OR rang=3 OR rang=4')
    return cursor.fetchall()

def GetListOfFirstFlow(nick,cursor):
    cursor.execute('SELECT nickname,second_rang FROM users WHERE rang=2 AND nickname!="'+nick+'"')
    return cursor.fetchall()

def GetListOfSecondFlow(nick,cursor):
    cursor.execute('SELECT nickname,second_rang FROM users WHERE rang=3')
    return cursor.fetchall()

def CreateProject(info,cursor,database):
    cursor.execute('INSERT INTO projects(title,type,status) VALUES ("'+info['name']+'",'+str(info['type'])+',"Сбор команды")')
    cursor.execute('SELECT id FROM projects WHERE title="'+info['name']+'"')
    project_id=cursor.fetchall()[0][0]
    cursor.execute('SELECT id FROM users WHERE nickname="' + info['leader'] + '"')
    leader_id=cursor.fetchall()[0][0]
    cursor.execute('INSERT INTO teams(user_id,project_id,role_id) VALUES('+str(leader_id)+','+str(project_id)+',1)')
    for i in range(0,len(info['experts'])):
        cursor.execute('SELECT id FROM users WHERE nickname="' + info['experts'][i] + '"')
        expert=cursor.fetchall()[0][0]
        cursor.execute('INSERT INTO teams(user_id,project_id,role_id) VALUES(' + str(expert) + ',' + str(project_id) + ',5)')
    database.commit()

def SetCurrentFighterVoting(voter_nick,counter,cursor,database):
    cursor.execute('UPDATE users SET curr_voting_id='+str(counter)+' WHERE nickname="'+voter_nick+'"')
    database.commit()

def GetCurrentFighterVoting(voter_nick,cursor):
    cursor.execute('SELECT curr_voting_id FROM users WHERE nickname="'+voter_nick+'"')
    return cursor.fetchall()[0][0]

def AddMark(nick_of_object,marks,axis,flow,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick_of_object+'"')
    id=cursor.fetchall()[0][0]
    string="|"
    for i in marks:
        string+=str(i)
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%Y")
    now_date='|'+now_date
    cursor.execute('INSERT INTO marks(user_id,axis,mark,mark_date,flow) VALUES ('+str(id)+','+str(axis)+',"'+string+'","'+now_date+'",'+str(flow)+')')
    cursor.execute('SELECT sum_of_marks FROM users WHERE nickname="' + nick_of_object + '"')
    summa = 0
    field = cursor.fetchall()[0][0]
    if (field != None):
        summa = int(field)
    for i in range(0, len(marks)):
        summa += marks[i]
    cursor.execute('UPDATE users SET sum_of_marks=' + str(summa) + ' WHERE nickname="' + nick_of_object + '"')
    database.commit()

def AddMarkFromProject(nick_of_object,marks,axis,flow,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick_of_object+'"')
    id=cursor.fetchall()[0][0]
    string="|"
    for i in marks:
        string=string+str(i*2)
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%Y")
    now_date='|'+now_date
    cursor.execute('INSERT INTO marks(user_id,axis,mark,mark_date,flow) VALUES ('+str(id)+','+str(axis)+',"'+string+'","'+now_date+'",'+str(flow)+')')
    cursor.execute('SELECT sum_of_marks FROM users WHERE nickname="' + nick_of_object + '"')
    summa = 0
    field = cursor.fetchall()[0][0]
    if (field != None):
        summa = float(field)
    for i in range(0, len(marks)):
        summa += float(marks[i])/2
    cursor.execute('UPDATE users SET sum_of_marks=' + str(summa) + ' WHERE nickname="' + nick_of_object + '"')
    database.commit()

def MarksOfFirstFlow(nick,cursor):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick+'"')
    id=cursor.fetchall()[0][0]
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user_id='+str(id)+' AND flow=1')
    return cursor.fetchall()

def MarksOfSecondFlow(nick,cursor):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick+'"')
    id=cursor.fetchall()[0][0]
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user_id='+str(id)+' AND flow=2')
    return cursor.fetchall()

def SetChatId(nick,chat_id,cursor,database):
    cursor.execute('UPDATE users SET chat_id='+str(chat_id)+' WHERE nickname="'+nick+'"')
    database.commit()

def GetChatId(nick,cursor):
    cursor.execute('SELECT chat_id FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchall()[0][0]

def IsThereActiveVoting(cursor):
    cursor.execute('SELECT * FROM voting WHERE status="active"')
    return len(cursor.fetchall())>0

def StartVoting(chat_id,user,number,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('INSERT INTO voting(chat_id,user,number_of_members,agree_number,disagree_number,start_date,status) values ("'+str(chat_id)+'","'+user+'",'+str(number)+
                   ',0,0,"'+now_date+'","active")')
    database.commit()

def GetUserWhoStartedVoting(cursor):
    cursor.execute('SELECT user FROM voting WHERE status="active"')
    return cursor.fetchall()[0][0]

def FinishVoting(cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE voting SET finish_date="'+now_date+'" WHERE status="active"')
    cursor.execute('UPDATE voting SET status="finished" WHERE status="active"')
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

def IsInProject(nick,cursor):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick+'"')
    id=cursor.fetchall()[0][0]
    cursor.execute('SELECT project_id FROM teams WHERE user_id='+str(id))
    return len(cursor.fetchall())>0

def IsUserTeamlead(nick,cursor):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick+'"')
    id=cursor.fetchall()[0][0]
    cursor.execute('SELECT project_id FROM teams WHERE user_id='+str(id)+' AND role_id=1')
    return len(cursor.fetchall())>0

def GetProjects(nick,cursor):
    cursor.execute('SELECT projects.title,teams.project_id FROM users,projects,teams WHERE users.nickname="' + nick + '" AND teams.user_id=users.id AND teams.project_id=projects.id GROUP BY projects.title')
    return cursor.fetchall()

def GetAllProjects(cursor):
    cursor.execute('SELECT title FROM projects')
    return cursor.fetchall()

def GetProject(title,cursor):
    cursor.execute('SELECT teams.project_id FROM teams,projects WHERE teams.project_id=projects.id AND projects.title="'+title+'"')
    return cursor.fetchall()[0][0]

def GetProjectInfo(id,cursor):
    info=''
    cursor.execute('SELECT projects.title,projects.status FROM projects,teams,users WHERE teams.project_id='+str(id)+' AND projects.id=teams.project_id ')
    arr=cursor.fetchall()[0]
    info+='Проект <i>"'+str(arr[0])+'"</i>. Статус: '+str(arr[1])+'\n<b>Состав команды:</b>\n'
    cursor.execute('SELECT users.nickname,roles.title FROM projects,teams,users,roles WHERE teams.project_id='+str(id)+' AND users.id=teams.user_id AND teams.role_id!=5 AND teams.role_id=roles.id GROUP BY users.nickname')
    arr=cursor.fetchall()
    for i in range(0,len(arr)):
        info+=arr[i][0]+', роль: '+arr[i][1]+'\n'
    cursor.execute('SELECT users.nickname FROM projects,teams,users WHERE teams.project_id='+str(id)+' AND users.id=teams.user_id AND teams.role_id=5 GROUP BY users.nickname')
    arr = cursor.fetchall()
    if(len(arr)==0):
        info+='В данном проекте нет экспертов'
    else:
        info+='<b>Эксперты:</b>\n'
        for i in range(0, len(arr)):
            info+=arr[i][0]+'\n'
    return info

def SetCurrProject(id,nick,cursor,database):
    cursor.execute('UPDATE users SET curr_editing_project='+str(id)+' WHERE nickname="'+nick+'"')
    database.commit()

def GetCurrProject(nick,cursor):
    cursor.execute('SELECT curr_editing_project FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchall()[0][0]

def AddToProject(project_id,nick,role,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="'+nick+'"')
    user_id=cursor.fetchall()[0][0]
    cursor.execute('INSERT INTO teams(project_id,user_id,role_id) VALUES('+str(project_id)+','+str(user_id)+','+str(role)+')')
    database.commit()

def GetMembersOfProject(project_id,cursor):
    cursor.execute('SELECT users.nickname FROM users,teams WHERE users.id=teams.user_id AND teams.role_id!=1 AND teams.role_id!=5 AND teams.project_id='+str(project_id))
    return cursor.fetchall()

def GetMembersOfProjectForVoting(nick,project_id,cursor):
    cursor.execute('SELECT users.nickname FROM users,teams WHERE users.id=teams.user_id AND teams.role_id!=5 AND teams.project_id='+str(project_id)+' AND users.nickname!="'+nick+'"')
    return cursor.fetchall()

def GetProjectById(project_id,cursor):
    cursor.execute('SELECT title FROM projects WHERE id='+str(project_id))
    return cursor.fetchall()[0][0]

def DeleteUserFromProject(user,project,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="'+user+'"')
    id=cursor.fetchall()[0][0]
    cursor.execute('DELETE FROM teams WHERE user_id='+str(id)+' AND project_id='+str(project))
    database.commit()

def ChangeStatusProject(status,project,cursor,database):
    cursor.execute('UPDATE projects SET status="'+status+'" WHERE id='+str(project))
    database.commit()

def GetInvestors(nick,cursor):
    cursor.execute('SELECT chat_id FROM users WHERE rang=8 AND nickname!="'+nick+'"')
    return cursor.fetchall()

def GetTitleOfRang(rang,cursor):
    cursor.execute('SELECT title FROM rangs WHERE id='+str(rang))
    return cursor.fetchall()[0][0]

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

def GetAuthority(user,cursor):
    cursor.execute('SELECT authority FROM users WHERE nickname="'+user+'"')
    return cursor.fetchall()[0][0]

def InviteInvestor(nick,cursor,database):
    cursor.execute('INSERT INTO users(nickname,rang) VALUES ("'+nick+'",12)')
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