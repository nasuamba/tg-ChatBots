import markup, dic, main


def help_msg(bot, user_id, msg):
    mess = f'бот: @GPNS_expert_bot' \
           f'\nnuser id: {user_id}' \
           f'\n' \
           f'\nсообщение: {msg}'
    to_chat_id = 'test'
    bot.send_message(to_chat_id, mess)

    mess = 'спасибо 🙏' \
           '\nмы постараемся связаться с вами как можно скорее'
    bot.send_message(user_id, mess, reply_markup = markup.simple_back_markup)