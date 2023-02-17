import sqlite3
import pandas as pd

EXPERTS_FULL = pd.read_excel("data.XLSX", sheet_name="эксперты")
EXPERTS_VERY_FULL = pd.read_excel("data.XLSX", sheet_name="эксперты с замами")
EXPERTS_ZAM = pd.read_excel("data.XLSX", sheet_name="замещающие")
EXPERTS_LIST = pd.read_excel("data.XLSX", sheet_name="список")
EXPERTS_BY_STEPS = pd.read_excel("data.XLSX", sheet_name="распределение")

# создаем БД
db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)

# создаем курсор
c = db.cursor()

# создаем пользовательскую таблицу
c.execute("""CREATE TABLE IF NOT EXISTS user_info (
             время_обращения DATETIME DEFAULT ((DATETIME('now'))),
             ID TEXT NOT NULL,
             имя TEXT,
             фамилия TEXT,
             задача TEXT)""")

# создаем таблицу для подбора экспертов (толькоо основные)
c.execute("""CREATE TABLE IF NOT EXISTS exp_frame (
             division TEXT,
             name TEXT,
             role TEXT,
             step TEXT,
             to_do TEXT)""")

# создаем таблицу для поиска по имени (вместе с замами)
c.execute("""CREATE TABLE IF NOT EXISTS full_exp_frame (
             division TEXT,
             name TEXT,
             role TEXT,
             step TEXT,
             to_do TEXT)""")

# создаем таблицу
c.execute("""CREATE TABLE IF NOT EXISTS for_send (
             division TEXT,
             name TEXT,
             role TEXT,
             step TEXT,
             to_do TEXT)""")

# создаем таблицу
c.execute("""CREATE TABLE IF NOT EXISTS alternate (
             division TEXT,
             name TEXT,
             zam TEXT)""")

# создаем таблицу
c.execute("""CREATE TABLE IF NOT EXISTS exp_list (
             password TEXT,
             name TEXT)""")

# создаем таблицу
c.execute("""CREATE TABLE IF NOT EXISTS exp_by_steps (
             role TEXT,
             step TEXT)""")


for i in range(EXPERTS_FULL['заказчик'].count()):
    c.execute('INSERT INTO exp_frame (division, name, role, step, to_do) VALUES (?, ?, ?, ?, ?)', 
    (EXPERTS_FULL['заказчик'][i], EXPERTS_FULL['имя'][i], EXPERTS_FULL['роль'][i], 
    EXPERTS_FULL['этап'][i], EXPERTS_FULL['Что нужно сделать?'][i])); 

for i in range(EXPERTS_VERY_FULL['заказчик'].count()):
    c.execute('INSERT INTO full_exp_frame (division, name, role, step, to_do) VALUES (?, ?, ?, ?, ?)', 
    (EXPERTS_VERY_FULL['заказчик'][i], EXPERTS_VERY_FULL['имя'][i], EXPERTS_VERY_FULL['роль'][i], 
    EXPERTS_VERY_FULL['этап'][i], EXPERTS_VERY_FULL['Что нужно сделать?'][i])); 

for i in range(EXPERTS_ZAM['имя'].count()):
    c.execute('INSERT INTO alternate (division, name, zam) VALUES (?, ?, ?)', 
    (EXPERTS_ZAM['заказчик'][i], EXPERTS_ZAM['имя'][i], EXPERTS_ZAM['замещающее лицо'][i])); 

for i in range(EXPERTS_LIST['имя'].count()):
    c.execute('INSERT INTO exp_list (password, name) VALUES (?, ?)', 
    (EXPERTS_LIST['№'][i], EXPERTS_LIST['имя'][i]))

for i in range(EXPERTS_BY_STEPS['роль'].count()):
    c.execute('INSERT INTO exp_by_steps (role, step) VALUES (?, ?)', 
    (EXPERTS_BY_STEPS['роль'][i], EXPERTS_BY_STEPS['этап'][i]))

#обновляем БД (после внесения любых изменений)
db.commit()

# закрываем соединение с базой
db.close()