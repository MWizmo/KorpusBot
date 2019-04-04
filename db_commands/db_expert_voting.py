# -*- coding: utf-8 -*-


def OrganizeExpertVoting(date, cursor, db):
    cursor.execute('INSERT INTO expert_voting(voting_date,status) VALUES("'+date+'","Preparing")')
    db.commit()


def GetCurrentPreparingExpertVoting(cursor):
    cursor.execute('SELECT id FROM expert_voting WHERE status="Preparing"')
    return cursor.fetchone()


def AddTeamleadToVoting(voting_id, lead_nick, cursor, db):
    cursor.execute('INSERT INTO voting_teamleads(voting_id,teamlead_nick) VALUES ('+str(voting_id)+',"'+lead_nick+'")')
    db.commit()


def GetDateOfPreparingExpertVoting(cursor):
    cursor.execute('SELECT voting_date FROM expert_voting WHERE status="Preparing"')
    return cursor.fetchone()[0]


def GetNumberOfAcceptedTeamleads(voting_id, cursor):
    cursor.execute('SELECT COUNT(*) FROM voting_teamleads WHERE voting_id='+str(voting_id))
    return cursor.fetchone()[0]


def ChangeDate(date, cursor, db):
    cursor.execute('UPDATE expert_voting SET voting_date="'+date+'" WHERE status="Preparing"')
    db.commit()


def GetListOfAcceptedTeamleads(voting_id, cursor):
    cursor.execute('SELECT teamlead_nick FROM voting_teamleads WHERE voting_id='+str(voting_id))
    return cursor.fetchall()


def StartExpertVoting(voting_id, experts_list, teamleads_list, cursor, db):
    for expert in experts_list:
        for teamlead in teamleads_list:
            cursor.execute('INSERT INTO expert_votings_info(voting_id,expert_nick,teamlead_nick,criterion,finished,mark) VALUES('+str(voting_id)+',"'+expert+'","'+
                           teamlead[0]+'",1,"No",0)')
            cursor.execute(
                'INSERT INTO expert_votings_info(voting_id,expert_nick,teamlead_nick,criterion,finished,mark) VALUES(' + str(
                    voting_id) + ',"' + expert + '","' +
                teamlead[0] + '",2,"No",0)')
            cursor.execute(
                'INSERT INTO expert_votings_info(voting_id,expert_nick,teamlead_nick,criterion,finished,mark) VALUES(' + str(
                    voting_id) + ',"' + expert + '","' +
                teamlead[0] + '",3,"No",0)')
            db.commit()


def GetNextExpertForVoting(teamlead, voting_id, cursor):
    cursor.execute('SELECT expert_nick FROM expert_votings_info WHERE teamlead_nick="'+teamlead+'" AND finished="No" AND voting_id='+str(voting_id))
    experts = cursor.fetchall()
    if len(experts) == 0:
        return 0
    else:
        return experts[0][0]


def GetMarkForTeamLeadOf(lead, voting_id, expert, criterion, cursor):
    cursor.execute('SELECT mark FROM expert_votings_info WHERE teamlead_nick="'+lead+
                   '" AND finished="No" AND voting_id='+str(voting_id)+' AND expert_nick="'+expert+'" AND criterion='+str(criterion))
    return cursor.fetchone()[0]


def GetFinishedMarkForTeamlead(lead, voting_id, expert, criterion, cursor):
    cursor.execute('SELECT mark FROM expert_votings_info WHERE teamlead_nick="'+lead+
                   '" AND finished="Yes" AND voting_id='+str(voting_id)+' AND expert_nick="'+expert+'" AND criterion='+str(criterion))
    return cursor.fetchone()[0]


def PutMarkForTeamLeadOf(lead, voting_id, expert, criterion, cursor, db):
    mark = GetMarkForTeamLeadOf(lead, voting_id, expert, criterion, cursor)
    if mark == '0' or mark == 0:
        mark = '1'
    else:
        mark = '0'
    cursor.execute('UPDATE expert_votings_info SET mark='+mark+' WHERE teamlead_nick="'+lead+
                   '" AND finished="No" AND voting_id='+str(voting_id)+' AND expert_nick="'+expert+'" AND criterion='+str(criterion))
    db.commit()


def AcceptMark(lead, voting_id, expert, cursor, db):
    cursor.execute('UPDATE expert_votings_info SET finished="Yes" WHERE teamlead_nick="' + lead +
                   '" AND finished="No" AND voting_id=' + str(voting_id) +
                   ' AND expert_nick="' + expert + '"')
    db.commit()


def ChangeVotingStatus(status, voting_id, cursor, db):
    cursor.execute('UPDATE expert_voting SET status="'+status+'" WHERE id='+str(voting_id))
    db.commit()


def IsThereActiveVoting(cursor):
    cursor.execute('SELECT * FROM expert_voting WHERE status="Started"')
    return len(cursor.fetchall()) > 0


def IsVotingFinished(voting_id, cursor):
    cursor.execute('SELECT * FROM expert_votings_info WHERE finished="No" AND voting_id=' + str(voting_id))
    return len(cursor.fetchall()) == 0


def CompileMarksOfExperts(voting_id, experts_list, teamleads_list, cursor, db):
    cursor.execute('SELECT voting_date FROM expert_voting WHERE id='+str(voting_id))
    time = cursor.fetchone()[0]
    for expert in experts_list:
        for i in range(1, 4):
            mark = 1
            for teamlead in teamleads_list:
                mark *= GetFinishedMarkForTeamlead(teamlead[0], voting_id, expert, i, cursor)
            cursor.execute('INSERT INTO expert_marks(expert,mark_date,criterion,mark) VALUES("'+expert+'","'+time+'",'+str(i)+','+str(mark)+')')
            db.commit()

