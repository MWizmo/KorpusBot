# -*- coding: utf-8 -*-


def GetLastVotingsByProject(project_id, cursor):
    cursor.execute('SELECT id,voting_date FROM votings WHERE project_id=' + str(
        project_id) + ' AND status="Finished" ORDER BY ID DESC')
    return cursor.fetchone()


def GetNextVotingDateByProject(project_id, cursor):
    cursor.execute('SELECT id,voting_date FROM votings WHERE project_id=' + str(project_id) + ' AND status="Preparing"')
    return cursor.fetchone()


def OrganizeNewVoting(project_id, cursor, db):
    cursor.execute('SELECT id FROM votings WHERE project_id=' + str(project_id) + ' AND status="Preparing"')
    if len(cursor.fetchall()) > 0:
        pass
    else:
        cursor.execute('INSERT INTO votings(project_id,status) VALUES(' + str(project_id) + ',"Preparing")')
        db.commit()


def GetCurrentPreparingVoting(project_id, cursor):
    cursor.execute('SELECT id,status FROM votings WHERE project_id=' + str(project_id) + ' AND (status="Preparing" or status="Started")')
    res = cursor.fetchone()
    return res[0], res[1]


def SetEditingVoting(user_id, id, cursor, db):
    cursor.execute('UPDATE users SET curr_editing_voting=' + str(id) + ' WHERE id=' + str(user_id))
    db.commit()


def GetEditingVoting(user_id, cursor):
    cursor.execute('SELECT curr_editing_voting FROM users WHERE id=' + str(user_id))
    return cursor.fetchone()[0]


def GetProjectIdByPreparingVotingId(voting_id, cursor):
    cursor.execute('SELECT project_id FROM votings WHERE id=' + str(voting_id))
    return cursor.fetchone()[0]


def GetExpertsFromVoting(voting_id, axis, cursor):
    cursor.execute('SELECT expert_id,confirmed FROM votings_experts WHERE axis=' + str(axis) + ' AND voting_id=' + str(
        voting_id) + ' AND confirmed<>"Denied"')
    return cursor.fetchall()


def SetDate(voting_id, date, cursor, db):
    cursor.execute('UPDATE votings SET voting_date="' + date + '" WHERE id=' + str(voting_id))
    db.commit()


def AddExpertToVoting(expert_id, voting_id, axis, cursor, db):
    cursor.execute('INSERT INTO votings_experts(voting_id,expert_id,axis,confirmed) VALUES (' +
                   str(voting_id) + ',' + str(expert_id) + ',' + str(axis) + ', "Not confirmed")')
    db.commit()


def ExpertDecisedInVoting(id, voting_id, axis, verdict, cursor, db):
    cursor.execute(
        'UPDATE votings_experts SET confirmed="' + verdict + '" WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(
            axis) + ' AND expert_id=' + str(id))
    db.commit()


def IsVotingPreparing(project_id, voting_id, cursor):
    cursor.execute('SELECT * FROM votings WHERE id=' + str(voting_id) + ' AND project_id=' + str(
        project_id) + ' AND status="Preparing"')
    return len(cursor.fetchall()) > 0


def IsVotingStarted(project_id, voting_id, cursor):
    cursor.execute('SELECT * FROM votings WHERE id=' + str(voting_id) + ' AND project_id=' + str(
        project_id) + ' AND status="Started"')
    return len(cursor.fetchall()) > 0


def IsVotingReadyForStart(voting_id, cursor):
    cursor.execute('SELECT * FROM votings_experts WHERE voting_id=' + str(voting_id) + ' AND confirmed="Accepted"')
    a = len(cursor.fetchall()) > 0
    cursor.execute('SELECT * FROM votings WHERE id=' + str(voting_id) + ' AND voting_date IS NOT NULL')
    b = len(cursor.fetchall()) > 0
    return a and b


def StartVoting(voting_id, cursor, db):
    cursor.execute('UPDATE votings SET status="Started" WHERE id=' + str(voting_id))
    cursor.execute('DELETE FROM votings_experts WHERE confirmed <>"Accepted"')
    db.commit()


def PutEmptyMark(voting_id, expert_id, cadet_id, axis, cursor, db):
    cursor.execute('INSERT INTO votings_info(voting_id,axis,expert_id,cadet_id,criterion,finished, mark) VALUES (' +
                   str(voting_id) + ',' + str(axis) + ',' + str(expert_id) + ',' + str(cadet_id) + ',1,"No",0),(' +
                   str(voting_id) + ',' + str(axis) + ',' + str(expert_id) + ',' + str(cadet_id) + ',2,"No",0),(' +
                   str(voting_id) + ',' + str(axis) + ',' + str(expert_id) + ',' + str(cadet_id) + ',3,"No",0)')
    db.commit()


def DifferenceInDays(date1, date2):
    import datetime
    d1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M')
    d2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M')
    return 365 * abs(d1.year - d2.year) + 30 * abs(d1.month - d2.month) + abs(d1.day - d2.day)


def IsPossibleToVoteAuthorityAxis(vot_date, expert_id, cadet_id, cursor):
    cursor.execute(
        'SELECT votings.voting_date  FROM votings_info,votings WHERE votings.id=votings_info.voting_id AND axis=3 AND expert_id='
        + str(expert_id) + ' AND cadet_id=' + str(cadet_id) + ' GROUP BY votings.voting_date')
    dates = cursor.fetchall()
    for date in dates:
        if date[0] is None:
            continue
        else:
            if DifferenceInDays(date[0], vot_date) <= 1:
                return False
    return True


def IsPossibleToVoteCommunicationAxis(vot_date, expert_id, cadet_id, cursor):
    cursor.execute(
        'SELECT votings.voting_date  FROM votings_info,votings WHERE votings.id=votings_info.voting_id AND axis=1 AND expert_id='
        + str(expert_id) + ' AND cadet_id=' + str(cadet_id) + ' GROUP BY votings.voting_date')
    dates = cursor.fetchall()
    for date in dates:
        if date[0] is None:
            continue
        else:
            if DifferenceInDays(date[0], vot_date) <= 1:
                return False
    return True


def GetDateOfVoting(voting_id, cursor):
    cursor.execute('SELECT voting_date FROM votings WHERE id=' + str(voting_id))
    return cursor.fetchone()[0]


def GetNonvotedCadetsForExpert(voting_id, expert_id, axis, cursor):
    cursor.execute('SELECT cadet_id FROM votings_info WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
                   ' AND expert_id=' + str(expert_id) + ' AND finished="No" GROUP BY cadet_id')
    return cursor.fetchall()


def GetVotedCadetsForExpert(voting_id, expert_id, axis, cursor):
    cursor.execute('SELECT cadet_id FROM votings_info WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
                   ' AND expert_id=' + str(expert_id) + ' AND finished="Yes" GROUP BY cadet_id')
    return cursor.fetchall()


def PutMark(voting_id, expert, cadet, axis, criterion, mark, cursor, db):
    cursor.execute(
        'UPDATE votings_info SET mark=' + str(mark) + ' WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
        ' AND expert_id=' + str(expert) + ' AND cadet_id=' + str(cadet) + ' AND criterion=' + str(criterion))
    db.commit()


def AcceptMark(voting_id, expert, cadet, axis, cursor, db):
    cursor.execute(
        'UPDATE votings_info SET finished="Yes" WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
        ' AND expert_id=' + str(expert) + ' AND cadet_id=' + str(cadet))
    db.commit()


def GetMarkInVoting(voting_id, expert, cadet, axis, criterion, cursor):
    cursor.execute('SELECT mark FROM votings_info  WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
                   ' AND expert_id=' + str(expert) + ' AND cadet_id=' + str(cadet) + ' AND criterion=' + str(criterion))
    return cursor.fetchone()[0]


def SetVotingCommentInfo(id, info, cursor, db):
    cursor.execute('UPDATE users SET curr_voting_comment=' + str(info) + ' WHERE id=' + str(id))
    db.commit()


def GetVotingCommentInfo(id, cursor):
    cursor.execute('SELECT curr_voting_comment FROM users WHERE id=' + str(id))
    return cursor.fetchone()[0]


def IsVotingFinished(voting_id, axis, cursor):
    cursor.execute(
        'SELECT * FROM votings_info WHERE voting_id=' + str(voting_id) + ' AND finished="No" AND axis=' + str(axis))
    return len(cursor.fetchall()) == 0


def CompileMarksByAxis(voting_id, axis, cursor, db):
    cursor.execute('SELECT voting_date FROM votings WHERE id=' + str(voting_id))
    time = cursor.fetchone()[0]
    cursor.execute('SELECT cadet_id FROM votings_info WHERE axis=' + str(axis) + ' AND voting_id=' + str(
        voting_id) + ' GROUP BY cadet_id')
    cadets = cursor.fetchall()
    if axis == 0:
        voted_dates = list()
        #voted_dates.append(time)
        cursor.execute('SELECT voting_date FROM votings')
        dates = cursor.fetchall()
        for date in dates:
            if date[0] is not None and DifferenceInDays(time, date[0]) <= 1:
                voted_dates.append(date[0])
        for cadet in cadets:
            for i in range(1, 4):
                summary_mark = 0
                for date in voted_dates:
                    cur_mark = 1
                    cursor.execute('SELECT id FROM votings WHERE voting_date="' + date + '"')
                    voting_id = cursor.fetchone()[0]
                    cursor.execute(
                        'SELECT mark FROM votings_info WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
                        ' AND cadet_id=' + str(cadet[0]) + ' AND criterion=' + str(i))
                    marks = cursor.fetchall()
                    for m in marks:
                        cur_mark *= int(m[0])
                    summary_mark += cur_mark
                cursor.execute('INSERT INTO marks(user_id,axis,criterion,mark,mark_date) VALUES (' + str(cadet[0]) + ',' +
                               str(axis) + ',' + str(i) + ',' + str(summary_mark) + ',"' + time + '")')
    else:
        for cadet in cadets:
            for i in range(1, 4):
                mark = 1
                cursor.execute(
                    'SELECT mark FROM votings_info WHERE voting_id=' + str(voting_id) + ' AND axis=' + str(axis) +
                    ' AND cadet_id=' + str(cadet[0]) + ' AND criterion=' + str(i))
                marks = cursor.fetchall()
                for m in marks:
                    mark *= int(m[0])
                if mark == 1 and axis == 3 and i == 1:
                    mark = 2
                if mark == 1 and axis == 3 and i == 2:
                    mark = 3
                cursor.execute('INSERT INTO marks(user_id,axis,criterion,mark,mark_date) VALUES (' + str(cadet[0]) + ',' +
                               str(axis) + ',' + str(i) + ',' + str(mark) + ',"' + time + '")')
    db.commit()


def FinishVoting(voting_id, cursor, db):
    cursor.execute('UPDATE votings SET status="Finished" WHERE id=' + str(voting_id))
    db.commit()


def PutExtraMarkForTeamlead(user_id, mark_date, cursor, db):
    cursor.execute(
        'INSERT INTO marks(user_id,axis,criterion,mark,mark_date) VALUES (' + str(user_id) + ',2,4,1,"' + mark_date + '")')
    db.commit()


def IsExpertInVoting(expert_id, voting_id, axis, cursor):
    cursor.execute('SELECT * FROM votings_experts WHERE expert_id='+str(expert_id)+' AND voting_id='+str(voting_id)+' AND axis='+str(axis))
    return len(cursor.fetchall()) > 0


def GetVotingsOfDay(date, cursor):
    cursor.execute('SELECT id,date FROM votings')
    all_dates = cursor.fetchall()
    votings = list()
    for _date in all_dates:
        if DifferenceInDays(date, _date[1]) <= 1:
            votings.append(_date[0])
    return votings