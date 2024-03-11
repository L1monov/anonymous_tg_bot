import telebot
from telebot import types

def reply_for_join_chat(tg_id, token_chat):
    reply = types.InlineKeyboardMarkup()
    join = types.InlineKeyboardButton(text='Присоединиться к чату', callback_data=f"join_chat|{tg_id}|{token_chat}" )
    reply.add(join)
    return reply

def reply_for_exit_chat(tg_id, chat):
    reply = types.InlineKeyboardMarkup()
    exit_chat_yes = types.InlineKeyboardButton(text='Да', callback_data=f"exit_chat_yes|{tg_id}|{chat}")
    exit_chat_no = types.InlineKeyboardButton(text='Нет', callback_data=f"exit_chat_no|{tg_id}|{chat}")
    reply.add(exit_chat_yes, exit_chat_no)
    return reply