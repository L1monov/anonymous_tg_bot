import pymysql
from config import db_name, password, host, user
import random
import string



conn = pymysql.connect(host=host, user=user, password=password,  db=db_name)
cursor = conn.cursor()

def get_info_user(tg_id):
    cursor.execute(
        f"""SELECT id, tg_id, first_name, nickname, last_name, rank, in_chat from user where tg_id = '{tg_id}'"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    user = [ids for ids in result_set][0]
    info_user = {
        'id': user[0],
        'tg_id': user[1],
        'first_name': user[2],
        'nickname': user[3],
        'last_name': user[4],
        'rank': user[5],
        'in_chat': user[6]
    }
    return info_user

def all_user():
    cursor.execute(
        f"""SELECT tg_id from user"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    users = [ids for ids in result_set]
    return users

def check_user(tg_id):
    cursor.execute(
        f"""SELECT tg_id from user where tg_id = '{tg_id}'"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    users = [ids for ids in result_set]
    if len(users) == 0:
        return True
    else:
        return False

def new_user(tg_id, first_name, last_name):
    if check_user(tg_id):
        cursor.execute(
            f"""insert into user (tg_id, nickname, first_name, last_name, rank)
                        values
                        ('{tg_id}','','{first_name}','{last_name}','executor')"""
        )

        # кладем результат в кортеж
        conn.commit()
        return ''
    else:
        return ''

def create_chat(description):
    cursor.execute(
        f"""select count(*) from chat_list"""
    )
    result = cursor.fetchall()
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    name_chat = f'chat_{str(int(result[0][0])+1)}'
    cursor.execute(
        f"""
            insert into chat_list (name_chat, token,description)
            values
            ('{name_chat}','{token}', '{description}');
            """
    )
    cursor.execute(
        f"""CREATE TABLE {name_chat} (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user VARCHAR(255),
                id_message VARCHAR(255),
                text VARCHAR(255),
                file VARCHAR(255),
                time VARCHAR(255)
            )"""
    )
    info ={
        'name_chat': name_chat,
        'token': token
    }
    return info


def set_nick_user(tg_id, nickname):
    cursor.execute(
            f"""
                update user set nickname = '{nickname}' where tg_id = '{tg_id}'
            """
    )
    conn.commit()

def get_info_chat(token_chat):
    try:
        cursor.execute(
            f"""select name_chat, description, members from chat_list where token = '{token_chat}'"""
        )
        result = cursor.fetchall()
    except:
        return 'Not found chat'
    if len(result) == 0:
        return 'Not found chat'
    result = result[0]
    info = {
        'name_chat': result[0],
        'description': result[1],
        'members_id': result[2].split(',')
    }
    if len(info['members_id']) == 0 or info['members_id'][0] == '':
        info['members_name'] = ['']
        return info
    list_id = ''
    for i in info['members_id']:
        list_id += f"{i},"

    list_id = list_id[:-1]

    cursor.execute(
        f"""select nickname from user 
        where 
        tg_id in ({list_id})"""
    )

    result_2 = cursor.fetchall()
    members_name = []
    for result in result_2:
        members_name.append(result[0])
    info['members_name'] = members_name
    return info


def check_user_chat(tg_id):
    cursor.execute(
        f"""SELECT in_chat from user where tg_id = '{tg_id}'"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    chat = [ids for ids in result_set]
    if len(chat) == 0:
        return True
    else:
        return False

def join_chat(tg_id, token_chat):
    cursor.execute(
        f"""select name_chat, description from chat_list where token = '{token_chat}'"""
    )
    result = cursor.fetchall()
    if len(result) == 0:
        return 'Not found chat'
    result = result[0]
    info = {
        'name_chat': result[0],
        'description': result[1]
    }
    cursor.execute(
        f"""update user set in_chat = '{info['name_chat']}' where tg_id = '{tg_id}'"""
    )
    cursor.execute(
        f"""update chat_list set members = CONCAT(members,'{tg_id}') where token = '{token_chat}'"""
    )
    conn.commit()
    return 'Join'

def exit_chat(tg_id, name_chat):
    cursor.execute(
        f"""update user set in_chat = '' where tg_id = '{tg_id}'"""
    )
    cursor.execute(
        f"""select members from chat_list where name_chat = '{name_chat}'"""
    )
    result_set = cursor.fetchall()
    chat = [ids for ids in result_set]
    print(len(chat[0]))
    if len(chat[0]) == 1:
        users = chat[0][0].replace(f"{tg_id}", '')
    else:
        users = chat[0][0].replace(f"{tg_id},", '')
    cursor.execute(
        f"""update chat_list set members = '{users}' where name_chat = '{name_chat}'"""
    )
    conn.commit()

def new_message(tg_id, message):
    cursor.execute(
        f"""SELECT in_chat, nickname from user where tg_id = '{tg_id}'"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    chat = [ids for ids in result_set][0]
    nick = chat[1]
    chat = chat[0]
    print(nick, chat)
    cursor.execute(
        f"""insert into {chat} (user, id_message, text)
                            values
                            ('{nick}','{message.id}','{message.text}')"""
    )

    conn.commit()



def get_info_members_for_send_message(chat, tg_id):
    cursor.execute(
        f"""SELECT members from chat_list where name_chat = '{chat}'"""
    )
    # кладем результат в кортеж
    result_set = cursor.fetchall()
    members = [ids for ids in result_set][0][0].split(',')
    return members

def get_all_message_chat(tg_id):
    chat = get_info_user(tg_id)['in_chat']
    cursor.execute(
        f"""
            select user, text from {chat}
        """
    )
    result_set = cursor.fetchall()
    messages = [ids for ids in result_set]
    info_message = {}
    count = 1
    for message in messages:
        info_message[count] = {
            'user': message[0],
            'message_text': message[1]
        }
        count += 1
    return info_message