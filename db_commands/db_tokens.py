# -*- coding: utf-8 -*-


def GetInvestmentTokens(id, cursor):
    cursor.execute('SELECT investment_tokens FROM users_tokens WHERE user_id ="' + id + '"')
    return float(cursor.fetchone()[0])


def AddInvestmentTokens(id, tokens, cursor, database):
    tokens += GetInvestmentTokens(id, cursor)
    cursor.execute('UPDATE users_tokens SET investment_tokens=' + str(tokens) + ' WHERE user_id=' + str(id))
    database.commit()


def ReduceInvestmentTokens(id, tokens, cursor, database):
    tokens -= GetInvestmentTokens(id, cursor)
    cursor.execute('UPDATE users_tokens SET investment_tokens=' + str((-1) * tokens) + ' WHERE user_id=' + str(id))
    database.commit()


def GetContributionTokens(id, cursor):
    cursor.execute('SELECT contribution_tokens FROM users_tokens WHERE user_id=' + str(id))
    return float(cursor.fetchone()[0])


def AddContributionTokens(id, tokens, cursor, database):
    tokens += GetContributionTokens(id, cursor)
    cursor.execute('UPDATE users_tokens SET contribution_tokens=' + str(tokens) + ' WHERE user_id=' + str(id))
    database.commit()


def ReduceContributionTokens(id, tokens, cursor, database):
    tokens -= GetContributionTokens(id, cursor)
    cursor.execute('UPDATE users_tokens SET contribution_tokens=' + str((-1) * tokens) + ' WHERE user_id=' + str(id))
    database.commit()


def OrganizeExchange(sender_id, destination_id, tokens, cursor, database):
    cursor.execute(
        'INSERT INTO exchanges(user_asker_id,user_destination_id,number_of_tokens,status) VALUES(' + str(
            sender_id) + ',' + str(destination_id) + ',' + str(
            tokens) + ',"In process")')
    database.commit()
    cursor.execute(
        'SELECT id FROM exchanges WHERE user_asker_id=' + str(sender_id) + ' AND user_destination_id=' + str(destination_id) + ' AND number_of_tokens=' + str(
            tokens) + ' AND status="In process"')
    return cursor.fetchone()[0]


def AcceptExchange(destination_id, id, cursor, database):
    cursor.execute('SELECT user_asker_id,number_of_tokens FROM exchanges WHERE id=' + str(id))
    cur = cursor.fetchone()
    asker = cur[0]
    tokens = cur[1]
    AddContributionTokens(asker, tokens, cursor, database)
    ReduceContributionTokens(destination_id, tokens, cursor, database)
    cursor.execute('UPDATE exchanges SET status="Accepted" WHERE id=' + str(id))
    database.commit()
    return asker


def DenyExchange(id, cursor, database):
    cursor.execute('SELECT user_asker_id FROM exchanges WHERE id=' + str(id))
    asker = cursor.fetchone()[0]
    cursor.execute('UPDATE exchanges SET status="Denied" WHERE id=' + str(id))
    database.commit()
    return asker
