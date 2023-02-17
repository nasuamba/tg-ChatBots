import sqlite3, config

# создаем БД
db = sqlite3.connect('db/mtr_bot.db', check_same_thread=False)

# создаем курсор
c = db.cursor()

# создаем таблицу для текста
# time DATETIME DEFAULT ((DATETIME('now'))),
c.execute("""CREATE TABLE IF NOT EXISTS mtr_inspection_1 (
             user_id TEXT,
             user_name TEXT,
             mtr_objekt TEXT,
             VC TEXT,
             VCP TEXT,
             sklad TEXT,
             DC TEXT,
             DCP TEXT,
             doc_date_from TEXT,
             doc_date_to TEXT)""")

comment = 'отсутствует'
# заполняем таблицу по одной конкретной аттестации (mtr_inspection_1)
for i in range(config.MTR['Наименование'].count()):
    mtr_objekt = f"{config.MTR['Наименование'][i]}; партия: {config.MTR['Партия'][i]}"
    c.execute(f"""INSERT INTO mtr_inspection_1 
    (mtr_objekt) 
    VALUES ('{mtr_objekt}')""")

#обновляем БД (после внесения любых изменений)
db.commit()
# закрываем соединение с базой
db.close()