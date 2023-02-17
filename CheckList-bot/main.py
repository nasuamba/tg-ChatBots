import telebot
import pymongo
import config, func, dic, kbd


bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending = True)


# подключение MongoDB
db_client = pymongo.MongoClient("mongodb+srv://nasuamba:Sokol366@myfirstcluster.znekeok.mongodb.net/test")
db = db_client["CheckList_PZD_KO"] # БД
c = db["Users"] # пользователи
c_CheckLists = db["CheckLists"] # чек листы
c_CheckBoxes = db["CheckBoxes"] # чек боксы


@bot.message_handler(commands = ["start"])
def start(message):

    mess = '🏠 Главное меню'
    bot.send_message(message.from_user.id, mess, reply_markup = kbd.welcome)


# существующие команды
comand_list = {'/start': start} 


@bot.callback_query_handler(func=lambda call: call.data.startswith('welcome'))
def verification(call):

    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    elif call.data.split('|')[1] == 'чек листы':
        if c.find_one({'user_id': call.from_user.id}) == None:
            mess = f'ваш профиль не найден'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.profile_create)
        else:
            mess = f'ваши Чек Листы'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.active_CL(call.from_user.id))
    elif call.data.split('|')[1] == 'личный кабинет':
        if c.find_one({'user_id': call.from_user.id}) == None:
            mess = f'ваш профиль не найден'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.profile_create)
        else:
            mess = func.PROFILE_SHOW(call.from_user.id)
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.Profile_show())


@bot.callback_query_handler(func = lambda call: call.data.startswith('role'))
def get_role(call):
    
    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    else:
        role = call.data.split('|')[1]
        func.DB_EDIT(c, 'user_id', call.from_user.id, 'роль', role)
        if c.find_one({'user_id': call.from_user.id}, {'user_id': 0, '_id': 0, 'роль': 0, 'телефон': 0, 'подразделение': 0}) == {}:
            mess = f'Выбрана роль: {role}' \
                   f'\n' \
                   f'\nКак к Вам обращаться?' \
                   f'\n' \
                   f'\n❗ Введите ФИО' \
                   f'\n💡 Образец: Путин Владимир Владимирович'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_name)
        else:
            mess = func.PROFILE_SHOW(call.from_user.id)
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.Profile_show())


@bot.message_handler()
def get_name(message):
    
    if message.text in comand_list: comand_list[message.text](message) # команды постоянного меню
    else:
        if len(message.text.split(' ')) == 3:
            name = message.text
            func.DB_EDIT(c, 'user_id', message.from_user.id, 'ФИО', name)
            if c.find_one({'user_id': message.from_user.id}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'подразделение': 0}) == {}:
                mess = f"Выбрана роль: {c.find_one({'user_id': message.from_user.id}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0})['роль']}" \
                       f'\nФИО: {name}' \
                       f'\n' \
                       f'\nКак с Вами связаться?' \
                       f'\n' \
                       f'\n❗ Введите мобильный номер' \
                       f'\n💡 Образец: +79111175131'
                bot.send_message(message.from_user.id, mess)
                bot.register_next_step_handler(message, get_phone)
            else:
                mess = func.PROFILE_SHOW(message.from_user.id)
                bot.send_message(message.from_user.id, mess, reply_markup = kbd.Profile_show())
        else:
            mess = f'❌ Некорректный ввод' \
                   f'\n💡 Образец: Путин Владимир Владимирович'
            bot.send_message(message.from_user.id, mess)
            bot.register_next_step_handler(message, get_name)


def get_phone(message):

    if message.text in comand_list: comand_list[message.text](message) # команды постоянного меню
    else:
        if len(message.text) == 12 and message.text[1:].isdigit():
            func.DB_EDIT(c, 'user_id', message.from_user.id, 'телефон', message.text)
            if c.find_one({'user_id': message.from_user.id}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'телефон': 0}) == {}:
                mess = 'Выберите Ваше подразделение:\n'
                for i in dic.units.items():
                    if i[0] == 14: mess += '\n'
                    mess += f'\n{i[0]}. {i[1]}'
                bot.send_message(message.from_user.id, mess, reply_markup = kbd.unit)
            else:
                mess = func.PROFILE_SHOW(message.from_user.id)
                bot.send_message(message.from_user.id, mess, reply_markup = kbd.Profile_show())
        else:
            mess = f'❌ Некорректный ввод' \
                   f'\n💡 Образец: +79111175131'
            bot.send_message(message.from_user.id, mess)
            bot.register_next_step_handler(message, get_phone)


@bot.callback_query_handler(func=lambda call: call.data.startswith('unit'))
def get_unit(call):

    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    else:
            func.DB_EDIT(c, 'user_id', call.from_user.id, 'подразделение', dic.units[int(call.data.split('|')[1])])
            mess = func.PROFILE_SHOW(call.from_user.id)
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.Profile_show())


@bot.callback_query_handler(func=lambda call: call.data.startswith('set'))
def profile_settings(call):
    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    else:
        if call.data.split('|')[1] == 'edit profile':
            mess = '⚙️ Настройки профиля'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.profile_set)

        elif call.data.split('|')[1] == 'role':
            mess = f'Укажите Вашу роль'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.role)

        elif call.data.split('|')[1] == 'name':
            mess = f'\nКак к Вам обращаться?' \
                   f'\n' \
                   f'\n❗ Введите ФИО' \
                   f'\n💡 Образец: Путин Владимир Владимирович'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_name)

        elif call.data.split('|')[1] == 'phone':
            mess = f'\nКак с Вами связаться?' \
                   f'\n' \
                   f'\n❗ Введите мобильный номер' \
                   f'\n💡 Образец: +79111175131'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_phone)

        elif call.data.split('|')[1] == 'unit':
            mess = 'Выберите Ваше подразделение:\n'
            for i in dic.units.items():
                if i[0] == 14: mess += '\n'
                mess += f'\n{i[0]}. {i[1]}'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.unit)

        elif call.data.split('|')[1] == 'close':
            mess = '🏠 Главное меню'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.welcome)

        elif call.data.split('|')[1] == 'create':
            mess = f'Укажите Вашу роль'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.role)

        elif call.data.split('|')[1] == 'delite profile':
            c.delete_one({'user_id': call.from_user.id})
            if c.find_one({'user_id': call.from_user.id}) == None: mess_1 = '✅ ваш профиль удален'
            else: mess_1 = 'не удалось удалить ваш профиль. пожалуйста, повторите попытку'
            bot.send_message(call.from_user.id, mess_1)

            mess = '🏠 Главное меню'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.welcome)
        
        elif call.data.split('|')[1] == 'RNP':
            mess = 'введите номер отбора (РНП)'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, change_RNP, call.data.split('|')[2])
        
        elif call.data.split('|')[1] == 'organizer':
            RNP = call.data.split('|')[2]
            mess = f'укажите ФИО организатора' \
                   f'\n' \
                   f'\n💡 Образец: Путин Владимир Владимирович'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_organizer, RNP)
        
        elif call.data.split('|')[1] == 'initiator':
            RNP = call.data.split('|')[2]
            mess = f'укажите ФИО инициатора' \
                   f'\n' \
                   f'\n💡 Образец: Путин Владимир Владимирович'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_initiator, RNP)


@bot.callback_query_handler(func=lambda call: call.data.startswith('CheckList'))
def CheckList_menu(call):

    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    
    elif call.data.split('|')[1] == 'create':
        if c.find_one({'user_id': call.from_user.id}) == None:
            mess = 'ваш профиль не найден. зарегистрируйтесь, чтобы получить доступ к чек листам'
            bot.send_message(call.from_user.id, mess, reply_markup = kbd.profile_create)
        else:
            mess = 'введите номер отбора (РНП)'
            bot.send_message(call.from_user.id, mess)
            bot.register_next_step_handler(call.message, get_RNP)

    elif call.data.split('|')[1] == 'open':
        RNP = call.data.split('|')[2]
        # создаем словарь для чекбокса. ключ - реестровый номер чек листа (РНП)
        if c_CheckBoxes.find_one({'РНП': RNP}) == None:
            dic.docs_dict[RNP] = {i: False for i in dic.docs_lst}
            dic.docs_dict[RNP]['РНП'] = RNP
            dic.docs_dict[RNP]['creator_id'] = call.from_user.id
            c_CheckBoxes.insert_one(dic.docs_dict[RNP])

        mess = f'✅ отметь выполненные шаги\n\n*чтобы узнать больше о шаге - выбери его в левом столбце'
        bot.send_message(call.from_user.id, mess, parse_mode = "HTML", reply_markup = kbd.ChekBox(RNP))

    elif call.data.split('|')[1] == 'delite CheckList':
        RNP = call.data.split('|')[2]
        c_CheckLists.delete_one({'РНП': RNP})
        c_CheckBoxes.delete_one({'РНП': RNP})
        if c_CheckLists.find_one({'РНП': RNP}) == None: mess_1 = '✅ чек лист удален'
        else: mess_1 = 'не удалось удалить чек лист. пожалуйста, повторите попытку'
        bot.send_message(call.from_user.id, mess_1)

        mess = '🏠 Главное меню'
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.welcome)

    elif call.data.split('|')[1] == 'doc':
        RNP = call.data.split('|')[2]
        mess = func.CHECK_LIST_SHOW(RNP)
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.CL_show(RNP))
    
    elif call.data.split('|')[1] == 'edit':
        RNP = call.data.split('|')[2]
        mess = '⚙️ Настройки Чек Листа'
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.CL_edit(RNP))
    
    elif call.data.split('|')[1] == 'close':
        RNP = call.data.split('|')[2]
        mess = func.CHECK_LIST_SHOW(RNP)
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.CL_show(RNP))


@bot.message_handler()
def get_RNP(message):
    if message.text in comand_list: comand_list[message.text](message) # команды постоянного меню
    else:
        RNP = message.text

        # если Чек Листа с таким номером нет в БД
        if c_CheckLists.find_one({'РНП': RNP}) == None:

            # проверяем, что профиль пользователя заполнен
            if c.find_one({'user_id': message.from_user.id}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0}) == {}:
                mess = 'в вашем профиле отсутствует роль'
                bot.send_message(message.from_user.id, mess)
                mess = func.PROFILE_SHOW(message.from_user.id)
                bot.send_message(message.from_user.id, mess, reply_markup = kbd.profile_set)

            # если заполняет организатор
            elif c.find_one({'user_id': message.from_user.id})['роль'] == 'организатор':
                c_CheckLists.insert_one({'РНП': RNP, 'организатор': c.find_one({'user_id': message.from_user.id})['ФИО'], 'creator_id': message.from_user.id})
                mess = f'укажите ФИО инициатора' \
                       f'\n' \
                       f'\n💡 Образец: Путин Владимир Владимирович'
                bot.send_message(message.from_user.id, mess)
                bot.register_next_step_handler(message, get_initiator, RNP)

            # если заполняет инициатор
            elif c.find_one({'user_id': message.from_user.id})['роль'] == 'инициатор':
                c_CheckLists.insert_one({'РНП': RNP, 'инициатор': c.find_one({'user_id': message.from_user.id})['ФИО'], 'creator_id': message.from_user.id})
                mess = f'укажите ФИО организатора' \
                       f'\n' \
                       f'\n💡 Образец: Путин Владимир Владимирович'
                bot.send_message(message.from_user.id, mess)
                bot.register_next_step_handler(message, get_organizer, RNP)
        
        # если Чек Лист с таким номером есть в БД
        else:
            name = c.find_one({'user_id': message.from_user.id})['ФИО']

            if c_CheckLists.find_one({'РНП': RNP})['организатор'] == name or c_CheckLists.find_one({'РНП': RNP})['инициатор'] == name:
                mess_1 = 'чек лист с таким РНП уже существует\nскорее всего, у вас указана другая роль'
                bot.send_message(message.from_user.id, mess_1)
                mess_2 = func.CHECK_LIST_SHOW(RNP)
                bot.send_message(message.from_user.id, mess_2, reply_markup = kbd.CL_show(RNP))
            else:
                mess = 'чек лист с таким РНП уже существует\nк сожалению, у вас нет к нему доступа'
                bot.send_message(message.from_user.id, mess_1, reply_markup = kbd.back_to_main)


def change_RNP(message, RNP):
    func.DB_EDIT(c_CheckLists, 'РНП', RNP, 'РНП', message.text)
    func.DB_EDIT(c_CheckBoxes, 'РНП', RNP, 'РНП', message.text)
    mess = func.CHECK_LIST_SHOW(message.text)
    bot.send_message(message.from_user.id, mess, reply_markup = kbd.CL_show(message.text))


def get_initiator(message, RNP):
    func.DB_EDIT(c_CheckLists, 'РНП', RNP, 'инициатор', message.text)
    mess = func.CHECK_LIST_SHOW(RNP)
    bot.send_message(message.from_user.id, mess, reply_markup = kbd.CL_show(RNP))


def get_organizer(message, RNP):
    func.DB_EDIT(c_CheckLists, 'РНП', RNP, 'организатор', message.text)
    mess = func.CHECK_LIST_SHOW(RNP)
    bot.send_message(message.from_user.id, mess, reply_markup = kbd.CL_show(RNP))


@bot.callback_query_handler(func=lambda call: call.data.startswith('back'))
def back(call):
    if call.data in comand_list: comand_list[call.data](call) # команды постоянного меню
    elif call.data.split('|')[1] == 'back_to_main_menu':
        mess = '🏠 Главное меню'
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.welcome)


@bot.callback_query_handler(func=lambda call: call.data.startswith('ChekBox'))
def CheckBox(call):
    # реакция на чекбокс
    x = call.data.split('|')[1]
    RNP = call.data.split('|')[2]
    if x[:1] == '✅' or x[:1] == '❌':
        # if dic.docs_dict[RNP][x[1:]]:
        if c_CheckBoxes.find_one({'РНП': RNP})[x[1:]]:
            func.DB_EDIT(c_CheckBoxes, 'РНП', RNP, x[1:], False)
        else: func.DB_EDIT(c_CheckBoxes, 'РНП', RNP, x[1:], True)

        bot.edit_message_text(chat_id = call.message.chat.id,
                              text = f'✅ отметь выполненные шаги\n\n*чтобы узнать больше о шаге - выбери его в левом столбце',
                              message_id = call.message.message_id,
                              parse_mode = "HTML",
                              reply_markup = kbd.ChekBox(RNP))

    
    elif x in dic.docs_lst:
        mess = dic.docs_info_dict[x]
        
        bot.edit_message_text(chat_id = call.message.chat.id,
                              text = mess,
                              message_id = call.message.message_id,
                              parse_mode = "HTML",
                              reply_markup = kbd.back_from_CheckBox(RNP))


    # В ГЛАВНОЕ МЕНЮ
    elif x == 'back_to_main_menu':
        bot.edit_message_text(chat_id = call.message.chat.id,
                              text = f'✅ отметь выполненные шаги\n\n*чтобы узнать больше о шаге - выбери его в левом столбце',
                              message_id = call.message.message_id,
                              parse_mode = "HTML",
                              reply_markup = kbd.ChekBox(RNP))

    
    elif x == 'back_to_CheckList':
        mess = func.CHECK_LIST_SHOW(RNP)
        bot.send_message(call.from_user.id, mess, reply_markup = kbd.CL_show(RNP))


if __name__ == '__main__':
    bot.polling(non_stop = True, interval = 0)