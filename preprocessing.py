# -*- coding: utf-8 -*-
import sqlite3

db = sqlite3.connect("korpus.db")
cursor = db.cursor()
cursor.execute('DROP TABLE rangs')
cursor.execute("""CREATE TABLE rangs(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL)""")
#
# cursor.execute("""CREATE TABLE users(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 			name TEXT,
# 			photo TEXT,
# 			rangs TEXT,
# 			authority float,
# 			nickname TEXT NOT NULL,
# 			registration_date TEXT ,
# 			email TEXT ,
# 			phone INTEGER,
# 			dossier TEXT,
# 			state INT,
# 			extra_info TEXT,
# 			sum_of_marks REAL,
# 			curr_voting_id INTEGER,
# 			chat_id INTEGER,
# 			curr_editing_project INTEGER,
# 			curr_editing_voting INTEGER,
# 			curr_voting_comment TEXT)""")
#
# cursor.execute('drop table users_tokens')
# cursor.execute('''CREATE TABLE users_tokens(
#     user_id INT PRIMARY KEY,
#     wallet TEXT,
#     contribution_tokens FLOAT,
#     investment_tokens FLOAT)''')
#
# cursor.execute('drop table exchanges')
# cursor.execute('''CREATE TABLE exchanges(
#     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#     user_asker_id INTEGER,
#     user_destination_id INTEGER,
#     number_of_tokens FLOAT,
#     status TEXT)''')

# cursor.execute('drop table marks')
# cursor.execute("""CREATE TABLE marks(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 			user_id INTEGER NOT NULL,
# 			axis INTEGER NOT NULL,
# 			criterion INTEGER NOT NULL,
# 			mark TEXT NOT NULL,
# 			mark_date TEXT NOT NULL)""")

# cursor.execute("""CREATE TABLE roles(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 			title varchar(20) NOT NULL)""")

# cursor.execute("""CREATE TABLE statuses(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 			status TEXT NOT NULL,
# 			comment TEXT)""")

# cursor.execute("""CREATE TABLE projects(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 			title TEXT NOT NULL,
# 			type TEXT NOT NULL,
# 			status INTEGER NOT NULL,
# 			documentation TEXT,
# 			annotation TEXT,
# 			foreign key(status) references statuses(id))""")

# cursor.execute("""CREATE TABLE teams(
#             user_id INTEGER not null,
# 			project_id INTEGER not null,
# 			role_id INTEGER not null,
# 			foreign key(user_id) references users(id),
# 			foreign key(project_id) references projects(id),
# 			foreign key(role_id) references roles(id))""")

# cursor.execute('drop table orders')
# cursor.execute("""CREATE TABLE orders(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
# 			type INTEGER NOT NULL,
# 			status TEXT NOT NULL)""")

# cursor.execute("""CREATE TABLE emission_data(
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             budget INTEGER NOT NULL,
# 			tokens_per_human FLOAT,
# 			status TEXT NOT NULL)""")

# cursor.execute("""CREATE TABLE votings(
#     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#     project_id INTEGER NOT NULL,
#     voting_date TEXT,
#     status TEXT)""")

# cursor.execute('drop table votings_experts')
# cursor.execute("""CREATE TABLE votings_experts(
#     voting_id INTEGER,
#     expert_id INTEGER,
#     axis INTEGER,
#     confirmed TEXT)""")
#
# cursor.execute('drop table votings_info')
# cursor.execute("""CREATE TABLE votings_info(
#     voting_id INTEGER NOT NULL,
#     axis INTEGER NOT NULL,
#     expert_id INTEGER,
#     cadet_id INTEGER,
#     criterion INTEGER,
#     mark INTEGER,
#     comment TEXT,
#     finished TEXT)""")

# cursor.execute("""CREATE TABLE expert_voting(
#     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#     voting_date TEXT,
#     status TEXT)""")

# cursor.execute('drop table voting_teamleads')
# cursor.execute("""CREATE TABLE voting_teamleads(
#     voting_id INTEGER NOT NULL,
#     teamlead_id INTEGER)""")
#
# cursor.execute('drop table expert_votings_info')
# cursor.execute("""CREATE TABLE expert_votings_info(
#     voting_id INTEGER NOT NULL,
#     expert_id INTEGER,
#     teamlead_id INTEGER,
#     criterion INTEGER,
#     mark INTEGER,
#     comment TEXT,
#     finished TEXT)""")
#
# cursor.execute('drop table expert_marks')
# cursor.execute("""CREATE TABLE expert_marks(
#     expert_id INTEGER,
#     mark_date TEXT,
#     criterion INTEGER,
#     mark INTEGER)""")

#################################################################

cursor.execute('INSERT INTO rangs (id,title) VALUES(1,"Абитуриент")')             # 1
cursor.execute('INSERT INTO rangs (title) VALUES("Первый курс")')                 # 2
cursor.execute('INSERT INTO rangs (title) VALUES("Второй курс")')                 # 3
cursor.execute('INSERT INTO rangs (title) VALUES("Третий курс")')                 # 4
cursor.execute('INSERT INTO rangs (title) VALUES("Тьютор")')                      # 5
cursor.execute('INSERT INTO rangs (title) VALUES("Преподаватель")')               # 6
cursor.execute('INSERT INTO rangs (title) VALUES("Трекер")')                      # 7
cursor.execute('INSERT INTO rangs (title) VALUES("Инвестор")')                    # 8
cursor.execute('INSERT INTO rangs (title) VALUES("Admin")')                       # 9
cursor.execute('INSERT INTO rangs (title) VALUES("Эксперт")')                     # 10
cursor.execute('INSERT INTO rangs (title) VALUES("Head teacher")')                # 11
cursor.execute('INSERT INTO rangs (title) VALUES("Приглашенный инвестор")')       # 12
cursor.execute('INSERT INTO rangs (title) VALUES("Приглашенный тьютор")')         # 13
cursor.execute('INSERT INTO rangs (title) VALUES("Приглашенный эксперт")')        # 14
cursor.execute('INSERT INTO rangs (title) VALUES("Приглашенный преподаватель")')  # 15
#
# #################################################################
#
# cursor.execute('INSERT INTO roles (id,title) VALUES(1,"Team Leader")')
# cursor.execute('INSERT INTO roles (title) VALUES("Hipster")')
# cursor.execute('INSERT INTO roles (title) VALUES("Hastler")')
# cursor.execute('INSERT INTO roles (title) VALUES("Hacker")')
# cursor.execute('INSERT INTO roles (title) VALUES("Expert")')

db.commit()

