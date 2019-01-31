# -*- coding: utf-8 -*-


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

def GetLeadProjects(nick,cursor):
    cursor.execute('SELECT projects.title,teams.project_id FROM users,projects,teams WHERE users.nickname="' + nick + '" AND teams.user_id=users.id AND teams.project_id=projects.id GROUP BY projects.title AND teams.role_id=1')
    return cursor.fetchall()

def GetExpertsFromProject(id,cursor):
    cursor.execute('SELECT users.nickname,users.id FROM projects,teams,users WHERE teams.project_id='+str(id)+' AND users.id=teams.user_id AND teams.role_id=5 GROUP BY users.nickname')
    return cursor.fetchall()

def GetTeamleadOfProject(id,cursor):
    cursor.execute('SELECT users.nickname FROM projects,teams,users WHERE teams.project_id=' + str(
        id) + ' AND users.id=teams.user_id AND teams.role_id=1 GROUP BY users.nickname')
    return cursor.fetchone()

def GetAllProjects(cursor):
    cursor.execute('SELECT title,id FROM projects')
    return cursor.fetchall()

def GetProject(title,cursor):
    cursor.execute('SELECT teams.project_id FROM teams,projects WHERE teams.project_id=projects.id AND projects.title="'+title+'"')
    return cursor.fetchall()[0][0]

def GetProjectTitle(id,cursor):
    cursor.execute('SELECT projects.title FROM teams,projects WHERE teams.project_id=projects.id AND projects.id=' + str(id))
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
    cursor.execute('SELECT users.nickname FROM users,teams WHERE users.id=teams.user_id AND teams.role_id!=5 AND teams.project_id='+str(project_id)+' GROUP BY users.nickname')
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

def AddExpertToProject(project_id,expert_nick,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="' + expert_nick + '"')
    expert_id = cursor.fetchall()[0][0]
    cursor.execute('INSERT INTO teams(user_id,project_id,role_id) VALUES(' + str(expert_id) + ',' + str(project_id) + ',5)')
    database.commit()