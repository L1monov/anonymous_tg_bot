import telebot
from telebot import types
from config import TOKEN_BOT, admins
import texts
import buttons
import db
import defs
bot = telebot.TeleBot(TOKEN_BOT)


@bot.message_handler(commands=['start', 'info'])
def start(message):
    if 'start' in message.text:
        info_user = defs.get_info_user_from_message(message)
        db.new_user(info_user['tg_id'],info_user['first_name'], info_user['last_name'])
        msg = texts.msg_for_start_bot
        bot.send_message(message.chat.id, msg , parse_mode='html')
    if 'info' in message.text:
        bot.send_message(message.chat.id, texts.msg_info, parse_mode='html')

@bot.message_handler(commands=['admin'])
def start(message):
    try:
        print(message.id)
        bot.delete_message(message.chat.id, 1)
        if defs.check_admin(defs.get_info_user_from_message(message)['tg_id']):
            msg = texts.msg_for_admin
            bot.send_message(message.chat.id, msg, parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор')
    except Exception as ex:
        print(f"Error start, {ex}")

@bot.message_handler(commands=['join_chat', 'create_chat', 'set_nick', 'exit_chat'])
def start(message):
    if 'join_chat' in message.text:
        tg_id = defs.get_info_user_from_message(message)['tg_id']
        if db.get_info_user(tg_id)['nickname'] == '' or  len(db.get_info_user(tg_id)['nickname']) == 0:
            bot.send_message(message.chat.id, 'У вас нет ника\nПридумайте его себе\n/set_nick *Имя*\nРекомендуем использовать Компания - Имя\nНапример: ICM - Рифат')
            return
        if db.get_info_user(tg_id)['in_chat'] != '':
            bot.send_message(message.chat.id, 'Вы уже находитесь в чате \nЧтобы выйти используйте /exit_chat')
            return
        token = message.text.split('/join_chat')[-1].replace(' ', '')

        if len(token) == 0:
            bot.send_message(message.chat.id, 'Вы не написали токен\n/join_chat *Токен*')
            return
        if db.get_info_chat(token) == 'Not found chat':
            bot.send_message(message.chat.id, 'Не нашли такого токена ((\nПроверьте токен')
            return
        else:
            info = db.get_info_chat(token)
            info_user = defs.get_info_user_from_message(message)
            msg = defs.create_message_info_chat(info)
            reply = buttons.reply_for_join_chat(info_user['tg_id'], token)
            bot.send_message(message.chat.id, msg, reply_markup=reply)

    if 'create_chat' in message.text:
        if defs.check_admin(defs.get_info_user_from_message(message)['tg_id']):
            tg_id = defs.get_info_user_from_message(message)['tg_id']
            desp = message.text.split('/create_chat')[-1]
            if desp:
                info_chat = db.create_chat(desp)
                name_chat =info_chat['name_chat']
                token_chat = info_chat['token']
                msg = f"Новый чат создан!\nНазвание чата: {name_chat}\nСекретный токен: <code>{token_chat}</code>\nНажмите на токен и отправьте участникам"
                bot.send_message(message.chat.id, msg, parse_mode= 'html' )
            if len(desp) <= 0:
                bot.send_message(message.chat.id, 'Нет навание чата')
        else:
            bot.send_message(message.chat.id, 'Вы не Администратор')

    if 'set_nick' in message.text:
        nickname = message.text.split('/set_nick')[-1]
        if len(nickname) == 0 or len(nickname) > 50:
            bot.send_message(message.chat.id, 'Проверьте правильность ввода\nВаш ник не должен быть больше 50 символов\nРекомендуем "Компания - Имя" Пример: *ICM - Рифат*')
            return
        else:
            db.set_nick_user(defs.get_info_user_from_message(message)['tg_id'], nickname)
            bot.send_message(message.chat.id, f'Ваш новый ник *{nickname}*\nТеперь вы можете присоединится к чату')

    if 'exit_chat' in message.text:
        tg_id = defs.get_info_user_from_message(message)['tg_id']
        if db.get_info_user(tg_id)['in_chat'] == '':
            bot.send_message(message.chat.id, 'Вы не состоите в чате')
            return
        else:
            chat = db.get_info_user(tg_id)['in_chat']
            reply = buttons.reply_for_exit_chat(tg_id, chat)
            bot.send_message(message.chat.id, 'Вы действительно хотите покинуть чат?', reply_markup=reply)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        first_param = call.data.split('|')[0]
    except Exception as ex:
        pass
    try:
        second_param = call.data.split('|')[1]
    except:
        pass
    try:
        third_param = call.data.split('|')[2]
    except:
        pass

    if first_param == 'join_chat':
        if db.get_info_user(second_param)['in_chat'] != '':
            bot.send_message(call.message.chat.id, 'Вы уже находитесь в чате \nЧтобы выйти используйте /exit_chat')
            return
        db.join_chat(second_param, third_param)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы успешно присоединились к чату")
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id - 1)
        info_messages = db.get_all_message_chat(second_param)
        for id_message in info_messages:
            msg = f"<b>Сообщение от {info_messages[id_message]['user']}</b>\n{info_messages[id_message]['message_text']}"
            bot.send_message(call.message.chat.id, msg, parse_mode='html')
    if first_param == 'exit_chat_yes':
        db.exit_chat(second_param, third_param)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы успешно вышли из чата")
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id - 1)
    if first_param == 'exit_chat_no':
        bot.delete_message(call.message.chat.id, call.message.id)

@bot.message_handler(content_types=['text'])
def func(message):
    tg_id = defs.get_info_user_from_message(message)['tg_id']
    chat_user = db.get_info_user(tg_id)['in_chat']
    nickname = db.get_info_user(tg_id)['nickname']
    # if chat_user != '':
    #     db.new_message(tg_id, message)
    #     msg = f"Сообщение от {nickname}\n{message.text}"
    #     for id_user in db.get_info_members_for_send_message(chat_user, tg_id):
    #         if id_user == str(tg_id):
    #             return
    #         try:
    #             bot.send_message(id_user, msg)
    #         except:
    #             pass


if __name__ == '__main__':
    print('bot rolling')
    bot.polling(none_stop=True)