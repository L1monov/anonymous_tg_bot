from config import admins
import telebot
from telebot import types

def check_admin(tg_id):
    if str(tg_id) in admins:
        return True
    else:
        return False

def get_info_user_from_message(message):
    tg_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    info_user = {
        'tg_id': tg_id,
        'first_name': first_name,
        'last_name': last_name
    }
    return info_user

def create_message_info_chat(info_chat):
    if info_chat['members_name'][0] == '':
        users = 'Пока нет пользователей'
    else:
        names = ''
        for name_user in info_chat['members_name']:
            names += f"{name_user}, "
        names = names[:-2]
        users = f"""Пользователи: {names}"""
    msg = f"""Информация о чате
Название: {info_chat['name_chat']}
Описание: {info_chat['description']}
{users}"""
    return msg
