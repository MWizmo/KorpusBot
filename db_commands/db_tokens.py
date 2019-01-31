# -*- coding: utf-8 -*-


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