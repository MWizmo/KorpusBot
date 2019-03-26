# -*- coding: utf-8 -*-

def GetLastVotingsByProject(project_id,cursor):
    cursor.execute('SELECT id,voting_date FROM votings WHERE project_id='+str(project_id)+' AND status="Finished" ORDER BY ID DESC')
    return cursor.fetchone()

def GetNextVotingDateByProject(project_id,cursor):
    cursor.execute('SELECT id,voting_date FROM votings WHERE project_id=' + str(project_id) + ' AND status="Preparing"')
    return cursor.fetchone()

def OrganizeNewVoting(project_id,cursor,db):
    cursor.execute('SELECT id FROM votings WHERE project_id='+str(project_id)+' AND status="Preparing"')
    if len(cursor.fetchall()) > 0:
        pass
    else:
       cursor.execute('INSERT INTO votings(project_id,status) VALUES('+str(project_id)+',"Preparing")')
       db.commit()

def GetCurrentPreparingVoting(project_id,cursor):
    cursor.execute('SELECT id FROM votings WHERE project_id=' + str(project_id) + ' AND status="Preparing"')
    return cursor.fetchone()[0]

def SetEditingVoting(nick,id,cursor,db):
    cursor.execute('UPDATE users SET curr_editing_voting='+str(id)+' WHERE nickname="'+nick+'"')
    db.commit()

def GetEditingVoting(nick,cursor):
    cursor.execute('SELECT curr_editing_voting FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchone()[0]

def GetProjectIdByPreparingVotingId(voting_id,cursor):
    cursor.execute('SELECT project_id FROM votings WHERE id=' + str(voting_id))
    return cursor.fetchone()[0]

def GetExpertsFromVoting(voting_id,axis,cursor):
    cursor.execute('SELECT expert_nick,confirmed FROM votings_experts WHERE axis='+str(axis)+' AND voting_id='+str(voting_id)+' AND confirmed<>"Denied"')
    return cursor.fetchall()

def SetDate(voting_id,date,cursor,db):
    cursor.execute('UPDATE votings SET voting_date="'+date+'" WHERE id='+str(voting_id))
    db.commit()

def AddExpertToVoting(nick, voting_id, axis, cursor, db):
    cursor.execute('INSERT INTO votings_experts(voting_id,expert_nick,axis,confirmed) VALUES ('+
                   str(voting_id)+',"'+nick+'",'+str(axis)+', "Not confirmed")')
    db.commit()

def ExpertDecisedInVoting(nick, voting_id, axis, verdict, cursor, db):
    cursor.execute('UPDATE votings_experts SET confirmed="'+verdict+'" WHERE voting_id='+str(voting_id)+' AND axis='+str(axis)+' AND expert_nick="'+nick+'"')
    db.commit()

def IsVotingPreparing(project_id, voting_id, cursor):
    cursor.execute('SELECT * FROM votings WHERE id='+str(voting_id)+' AND project_id='+str(project_id)+' AND status="Preparing"')
    return len(cursor.fetchall()) > 0

def IsVotingStarted(project_id, voting_id, cursor):
    cursor.execute('SELECT * FROM votings WHERE id='+str(voting_id)+' AND project_id='+str(project_id)+' AND status="Started"')
    return len(cursor.fetchall()) > 0

def IsVotingReadyForStart(voting_id,cursor):
    cursor.execute('SELECT * FROM votings_experts WHERE voting_id='+str(voting_id)+' AND confirmed="Accepted"')
    return len(cursor.fetchall()) > 0

def StartVoting(voting_id, cursor, db):
    cursor.execute('UPDATE votings SET status="Started" WHERE id='+str(voting_id))
    db.commit()

def PutEmptyMark(voting_id, expert, cadet, axis, cursor, db):
    cursor.execute('INSERT INTO votings_info(voting_id,axis,expert_nick,cadet_nick,criterion) VALUES ('+
                   str(voting_id)+','+str(axis)+',"'+expert+'","'+cadet+'",1),('+
                   str(voting_id)+','+str(axis)+',"'+expert+'","'+cadet+'",2),('+
                   str(voting_id)+','+str(axis)+',"'+expert+'","'+cadet+'",3)')
    db.commit()

def GetNonvotedCadetsForExpert(voting_id, expert, axis, cursor):
    cursor.execute('SELECT cadet_nick FROM votings_info WHERE voting_id='+str(voting_id)+' AND axis='+str(axis)+
                   ' AND expert_nick="'+expert+'" AND mark is Null GROUP BY cadet_nick')
    return cursor.fetchall()

def PutMark(voting_id, expert, cadet, axis, criterion, mark, cursor, db):
    cursor.execute('UPDATE votings_info SET mark='+str(mark)+' WHERE voting_id='+str(voting_id)+' AND axis='+str(axis)+
                   ' AND expert_nick="'+expert+'" AND cadet_nick="'+cadet+'" AND criterion='+str(criterion))
    db.commit()

def GetMarkInVoting(voting_id, expert, cadet, axis, criterion, cursor):
    cursor.execute('SELECT mark FROM votings_info  WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
        ' AND expert_nick="' + expert + '" AND cadet_nick="' + cadet + '" AND criterion=' + str(criterion))
    return cursor.fetchone()

def SetVotingCommentInfo(nick,info,cursor,db):
    cursor.execute('UPDATE users SET curr_voting_comment='+str(info)+' WHERE nickname="'+nick+'"')
    db.commit()

def GetVotingCommentInfo(nick,cursor):
    cursor.execute('SELECT curr_voting_comment FROM users WHERE nickname="'+nick+'"')
    return cursor.fetchone()[0]

