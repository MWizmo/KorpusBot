# -*- coding: utf-8 -*-
import sqlite3

db = sqlite3.connect("korpus.db")
cursor = db.cursor()

cursor.execute("""CREATE TABLE rangs(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL)""")

cursor.execute("""CREATE TABLE users(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			name TEXT,
			photo TEXT,
			rang INTEGER NOT NULL,
			authority float,
			nickname TEXT NOT NULL,
			balance float,
			registration_date TEXT ,
			email TEXT ,
			phone INTEGER,
			dossier TEXT,
			state INT,
			second_rang INTEGER,
			sum_of_marks REAL,
			curr_voting_id INTEGER,
			chat_id INTEGER,
			wallet TEXT,
			curr_editing_project INTEGER,
            foreign key(rang) references rangs(id))""")

cursor.execute("""CREATE TABLE marks(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER NOT NULL,
			axis INTEGER NOT NULL,
			mark TEXT NOT NULL,
			mark_date TEXT NOT NULL,
			flow INTEGER NOT NULL,
            foreign key (user_id) references users(id))""")

cursor.execute("""CREATE TABLE roles(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			title varchar(20) NOT NULL)""")

cursor.execute("""CREATE TABLE statuses(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			status TEXT NOT NULL,
			comment TEXT)""")

cursor.execute("""CREATE TABLE projects(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			type TEXT NOT NULL,
			status INTEGER NOT NULL,
			documentation TEXT,
			annotation TEXT,
			foreign key(status) references statuses(id))""")

cursor.execute("""CREATE TABLE teams(
            user_id INTEGER not null,
			project_id INTEGER not null,
			role_id INTEGER not null,
			foreign key(user_id) references users(id),
			foreign key(project_id) references projects(id),
			foreign key(role_id) references roles(id))""")

cursor.execute("""CREATE TABLE voting(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
			chat_id TEXT NOT NULL,
			number_of_members INTEGER NOT NULL,
			agree_number INTEGER NOT NULL,
			disagree_number INTEGER NOT NULL,
			start_date TEXT NOT NULL,
			finish_date TEXT,
			status TEXT NOT NULL)""")

cursor.execute("""CREATE TABLE orders(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
			type INTEGER NOT NULL,
			status TEXT NOT NULL)""")

#################################################################

cursor.execute('INSERT INTO rangs (id,title) VALUES(1,"Applicant")')
cursor.execute('INSERT INTO rangs (title) VALUES("First flow")')
cursor.execute('INSERT INTO rangs (title) VALUES("Fighter")')
cursor.execute('INSERT INTO rangs (title) VALUES("Veteran")')
cursor.execute('INSERT INTO rangs (title) VALUES("Tutor")')
cursor.execute('INSERT INTO rangs (title) VALUES("Educator")')
cursor.execute('INSERT INTO rangs (title) VALUES("Stalker")')
cursor.execute('INSERT INTO rangs (title) VALUES("Investor")')
cursor.execute('INSERT INTO rangs (title) VALUES("Admin")')
cursor.execute('INSERT INTO rangs (title) VALUES("Expert")')
cursor.execute('INSERT INTO rangs (title) VALUES("Head teacher")')
cursor.execute('INSERT INTO rangs (title) VALUES("Invited investor")')


#################################################################

cursor.execute('INSERT INTO roles (id,title) VALUES(1,"Team Leader")')
cursor.execute('INSERT INTO roles (title) VALUES("Hipster")')
cursor.execute('INSERT INTO roles (title) VALUES("Hastler")')
cursor.execute('INSERT INTO roles (title) VALUES("Hacker")')
cursor.execute('INSERT INTO roles (title) VALUES("Expert")')

db.commit()

