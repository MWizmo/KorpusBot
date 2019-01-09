# -*- coding: utf-8 -*-
import sqlite3
import datetime
from config import isRang

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


def UpdateExrtaInfo(nick,extra_info,cursor,database):
    cursor.execute('UPDATE users SET extra_info="' + extra_info + '" WHERE nickname="' + nick + '"')
    database.commit()


def BecomeBeginner(nick,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE users SET authority=0.0,balance=0.0,registration_date="'+now_date+'",sum_of_marks=0.0 WHERE nickname="'+nick+'"')
    database.commit()


def IsUserInDB(nick,cursor,database):
    cursor.execute('SELECT * FROM users WHERE nickname="'+nick+'"')
    response=cursor.fetchall()
    return len(response)>0


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

def AddRang(nick,rang,cursor,database):
    rangs=GetRangs(nick,cursor)
    if not (rang in rangs):
        rangs.append(rang)
        rang_str = listToRangs(rangs)
        cursor.execute('UPDATE users SET rangs="'+rang_str+'" WHERE nickname="'+nick+'"')
        database.commit()

def DeleteRang(nick,rang,cursor,database):
    rangs = GetRangs(nick, cursor)
    rangs.remove(rang)
    rang_str = listToRangs(rangs)
    cursor.execute('UPDATE users SET rangs="' + rang_str + '" WHERE nickname="' + nick + '"')
    database.commit()


def GetProfile(nick,cursor):
    if (nick[0] != '@'):
        nick = "@" + nick
    cursor.execute('SELECT name,phone,email,photo,authority,registration_date,sum_of_marks,dossier FROM users WHERE nickname="' + nick + '"')
    return cursor.fetchall()[0]

def GetName(nick,cursor):
    cursor.execute('SELECT name FROM users WHERE nickname="' + nick + '"')
    name = cursor.fetchone()[0]
    if name == None:
        return nick
    else:
        return name

def GetListOfUsers(cursor):
    cursor.execute('SELECT nickname,name,chat_id FROM users')
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

def AddExpertToProject(project_id,expert_nick,cursor,database):
    cursor.execute('SELECT id FROM users WHERE nickname="' + expert_nick + '"')
    expert_id = cursor.fetchall()[0][0]
    cursor.execute('INSERT INTO teams(user_id,project_id,role_id) VALUES(' + str(expert_id) + ',' + str(project_id) + ',5)')
    database.commit()

def SetCurrentFighterVoting(voter_nick,counter,cursor,database):
    cursor.execute('UPDATE users SET curr_voting_id='+str(counter)+' WHERE nickname="'+voter_nick+'"')
    database.commit()

def GetCurrentFighterVoting(voter_nick,cursor):
    cursor.execute('SELECT curr_voting_id FROM users WHERE nickname="'+voter_nick+'"')
    return cursor.fetchall()[0][0]

def AddMark(nick_of_object,marks,axis,number_of_evaluators,cursor,database):
    string="|"
    for i in marks:
        string+=str(i)
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%d/%m/%Y")
    now_date='|'+now_date
    cursor.execute('INSERT INTO marks(user,axis,mark,mark_date,status,number_evaluators) VALUES ("'+nick_of_object+'",'+str(axis)+',"'+
                   string+'","'+now_date+'","not confirmed",'+str(number_of_evaluators)+')')
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

def GetMarks(nick,cursor):
    cursor.execute('SELECT mark,axis,mark_date FROM marks WHERE user="'+nick+'" AND status="confirmed"')
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

def StartVoting(chat_id,user,number,summa,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('INSERT INTO voting(chat_id,user,number_of_members,agree_number,disagree_number,start_date,status) values ("'+str(chat_id)+'","'+user+'",'+str(number)+
                   ',0,0,"'+now_date+'","active")')
    cursor.execute('UPDATE emission_data SET status="not actual" WHERE status="accepted"')
    cursor.execute('INSERT INTO emission_data(budget,status) VALUES ('+str(summa)+',"voting")')
    database.commit()

def GetUserWhoStartedVoting(cursor):
    cursor.execute('SELECT user FROM voting WHERE status="active"')
    return cursor.fetchall()[0][0]

def FinishVoting(cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute('UPDATE voting SET finish_date="'+now_date+'" WHERE status="active"')
    cursor.execute('UPDATE voting SET status="finished" WHERE status="active"')
    cursor.execute('UPDATE emission_data SET status="accepted" WHERE status="voting"')
    database.commit()

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
    cursor.execute('SELECT users.nickname FROM users,teams WHERE users.id=teams.user_id AND teams.role_id!=5 AND teams.project_id='+str(project_id))
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

def StartCourseVoting(nick,cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    str='INSERT INTO course_votings(initiator,start_date,status) VALUES ("'+nick+'","'+now_date+'","Active")'
    cursor.execute('INSERT INTO course_votings(initiator,start_date,status) VALUES ("'+nick+'","'+now_date+'","Active")')
    database.commit()

def MayCoursantVote(cursor):
    cursor.execute('SELECT * FROM course_votings WHERE status="Active"')
    return len(cursor.fetchall()) > 0

def AreThereCourseVotings(cursor):
    cursor.execute('SELECT * FROM course_votings WHERE status="Active"')
    return len(cursor.fetchall()) > 0

def WhoStartedCourseVoting(cursor):
    cursor.execute('SELECT initiator FROM course_votings WHERE status="Active"')
    return cursor.fetchall()[0][0]

def FinishCourseVoting(cursor,database):
    now_date = datetime.datetime.today()
    now_date = now_date.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute("UPDATE course_votings SET status='Finished',finish_date='"+now_date+"' WHERE status='Active'")
    database.commit()

def SetDossier(dossier,nick,cursor,database):
    cursor.execute('UPDATE users SET dossier="'+dossier+'" WHERE nickname="'+nick+'"')
    database.commit()

def GetDossier(nick,cursor):
    cursor.execute('SELECT dossier FROM users WHERE nickname ="'+nick+'"')
    a=cursor.fetchone()[0]
    return a

def GetAllMarks(cursor):
    cursor.execute('SELECT sum_of_marks,nickname FROM users')
    return cursor.fetchall()

def GetInvestmentTokens(nick, cursor):
    cursor.execute('SELECT investment_tokens FROM users_tokens WHERE user ="' + nick + '"')
    return float(cursor.fetchone()[0])

def AddInvestmentTokens(nick, tokens, cursor, database):
    tokens+=GetInvestmentTokens(nick, cursor)
    cursor.execute('UPDATE users_tokens SET investment_tokens='+str(tokens)+' WHERE user ="' + nick + '"')
    database.commit()

def ReduceInvestmentTokens(nick, tokens, cursor, database):
    tokens -= GetInvestmentTokens(nick, cursor)
    cursor.execute('UPDATE users_tokens SET investment_tokens=' + str((-1)*tokens) + ' WHERE user ="' + nick + '"')
    database.commit()

def GetContributionTokens(nick, cursor):
    cursor.execute('SELECT contribution_tokens FROM users_tokens WHERE user ="' + nick + '"')
    return float(cursor.fetchone()[0])

def AddContributionTokens(nick, tokens, cursor, database):
    tokens+=GetContributionTokens(nick, cursor)
    cursor.execute('UPDATE users_tokens SET contribution_tokens='+str(tokens)+' WHERE user ="' + nick + '"')
    database.commit()

def ReduceContributionTokens(nick, tokens, cursor, database):
    tokens-=GetContributionTokens(nick, cursor)
    cursor.execute('UPDATE users_tokens SET contribution_tokens='+str((-1)*tokens)+' WHERE user ="' + nick + '"')
    database.commit()

def OrganizeExchange(sender,destination,tokens,cursor,database):
    cursor.execute('INSERT INTO exchanges(user_asker,user_destination,number_of_tokens,status) VALUES("'+sender+'","'+destination+'",'+str(tokens)+',"In process")')
    database.commit()
    cursor.execute('SELECT id FROM exchanges WHERE user_asker="'+sender+'" AND user_destination="'+destination+'" AND number_of_tokens='+str(tokens)+' AND status="In process"')
    return cursor.fetchone()[0]

def AcceptExchange(destination,id,cursor,database):
    cursor.execute('SELECT user_asker,number_of_tokens FROM exchanges WHERE id='+str(id))
    cur=cursor.fetchone()
    asker=cur[0]
    tokens=cur[1]
    AddContributionTokens(asker,tokens,cursor,database)
    ReduceContributionTokens(destination,tokens,cursor,database)
    cursor.execute('UPDATE exchanges SET status="Accepted" WHERE id='+str(id))
    database.commit()
    return asker

def DenyExchange(id,cursor,database):
    cursor.execute('SELECT user_asker FROM exchanges WHERE id=' + str(id))
    asker=cursor.fetchone()[0]
    cursor.execute('UPDATE exchanges SET status="Denied" WHERE id=' + str(id))
    database.commit()
    return asker

def StartEvaluateInProject(project_id,user_voter,axis,marks,user_evaluator,cursor,database):
    user_marks=""
    for mark in marks:
        user_marks = user_marks + str(mark) + '|'
    if user_evaluator[0]!='@':
        user_evaluator=user_evaluator[0]
    cursor.execute('INSERT INTO project_voting(project_id,user_voter,axis,marks,user_evaluator) VALUES('+str(project_id)+',"'+user_voter+
                   '",'+str(axis)+',"'+user_marks+'","'+user_evaluator+'")')
    database.commit()

def EvaluateInProject(project_id,user_voter,axis,user_evaluator,verdict,cursor,database):
    cursor.execute('UPDATE project_voting SET verdict="'+verdict+'" WHERE project_id='+str(project_id)+' AND user_voter="'+user_voter+
                   '" AND axis='+str(axis)+' AND user_evaluator="'+user_evaluator+'" AND verdict is Null')
    if verdict == 'disagree':
        cursor.execute('DELETE FROM marks WHERE status="not confirmed" AND user="'+user_voter+'" AND axis='+str(axis))
    else:
        cursor.execute('SELECT number_evaluators FROM marks WHERE status="not confirmed" AND user="'+user_voter+'" AND axis='+str(axis))
        num = int(cursor.fetchone()[0])
        num -= 1
        cursor.execute('UPDATE marks SET number_evaluators='+str(num)+' WHERE status="not confirmed" AND user="' + user_voter + '" AND axis=' + str(axis))
        if num == 0:
            cursor.execute('UPDATE marks SET status="confirmed" WHERE status="not confirmed" AND user="' + user_voter + '" AND axis=' + str(axis))
            return 1
    database.commit()
    return 0

def ExplainEvaluationInProject(axis,user_evaluator,explanation,cursor,database):
    cursor.execute('SELECT project_id, user_voter FROM project_voting WHERE axis=' + str(axis)
                   + ' AND user_evaluator="' + user_evaluator + '" AND verdict="disagree" AND explanation is Null')
    elems = cursor.fetchone()
    id = elems[0]
    user = elems[1]
    cursor.execute('UPDATE project_voting SET explanation="' + explanation + '" WHERE axis=' + str(axis)
                   + ' AND user_evaluator="' + user_evaluator + '" AND verdict="disagree" AND explanation is Null')
    database.commit()
    return id, user
