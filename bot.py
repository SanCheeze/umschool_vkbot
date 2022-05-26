# -*- coding: utf-8 -*-
import os

from time import sleep
import requests
import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from keyboard import menu_keyboard, inline_keyboard

# from configparser import ConfigParser

TOKEN = 'token'
vk_session = vk_api.VkApi(token=TOKEN)
vk_upload = VkUpload(vk_session)
longpoll = VkBotLongPoll(vk_session, 193110116)

answering = False
answering_index = 0
questions = []
questions_list = []

vk = vk_session.get_api()

bad_words = ['some', 'bad', 'words']


# Функция получения ID рабочих групп и bad_words
# def parse():
#     config = ConfigParser().read('data.ini')
#     workgroups = config['WorkGroups']
#     bad_words_ = config['BadWords']
#
#     return workgroups['reports_id'], workgroups['questions_id'], workgroups['main_groups_id'], bad_words_['bad_words']
#
#
# reports_id, questions_id, maingroups, bad_words = parse()


# Функция отправки сообщения от лица бота
def sender(cht_id, text, fwd_mess=None, att=None, kb=None):
    attachments = []

    if att:
        attachments = get_images(att[0])

    vk_session.method('messages.send', {
        'chat_id': cht_id,
        'message': text,
        'random_id': 0,
        'forward_messages': [fwd_mess],
        'attachment': ','.join(attachments),  # ','.join(attachments)
        'keyboard': kb
    })


def add_question(cht_id, needed_user_id, username, mess):
    global questions
    questions.append(
        {
            'chat_id': cht_id,
            'username': f"@id{needed_user_id}({username['first_name']} {username['last_name']})",
            'text': mess
        }
    )


# Скачиваем картинку, которую отправил пользователь
def get_images(data):
    attachments = []

    for data_list in data:
        with open(fr'{os.getcwd()}/images/answer.jpg', 'wb') as image:
            url = data_list['photo']['sizes'][-1]['url']
            img = requests.get(url)
            image.write(img.content)

        upload_image = vk_upload.photo_messages(photos=fr'{os.getcwd()}/images/answer.jpg')[0]
        attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')

        os.remove(os.getcwd() + fr'/images/answer.jpg')
    return attachments


# Функция для ответа на вопрос ученика
def answer(index, mess, attachments=None):
    username = questions[index]['username']
    sender(5, f'{username}, ответ на твой вопрос:'
              f'\n"{mess}"', att=attachments)


# Функция для ответа на вопрос ученика
def question(user_id, user, mess, attachments):
    sender(1, f'@id{user_id} ({user["first_name"]} {user["last_name"]}) задаёт вопрос:\n"{mess}"',
           att=attachments, kb=menu_keyboard)
    sender(chat_id, f'@id{user_id} ({user["first_name"]} {user["last_name"]}), твой вопрос'
                    f' сейчас рассматривается)')
    add_question(chat_id, user_id, user, mess)


# Находим название чата
def get_chat_name_by_id(cht_id):
    return vk.messages.getConversationsById(peer_ids=2000000000 + cht_id)


# Отправка репорта
def forward_report(cid, name, username, mess):
    sender(cht_id=cid, text=f'Название беседы: {name}\nПользователь: {username}', fwd_mess=mess)


# Ловец сообщений
while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:

                # Получаем данные о сообщении, чате и пользователе
                msg = event.object.message['text']
                chat_id = event.chat_id
                user_id = event.object.message['from_id']
                user = vk.users.get(user_id=user_id)[0]

                # Находим название чата
                chat = get_chat_name_by_id(chat_id)

                message_id = chat['items'][0]['last_message_id']
                current_message = vk.messages.getById(message_ids=message_id)['items'][0]

                # Управление чатом с вопросами
                if chat_id == 1:

                    try:
                        splited_answer = msg.split('[club193110116|@change___it] ')
                        del splited_answer[0]
                        if questions_list[int(splited_answer[0]) - 1]:
                            sender(1, 'Пишите ответ:')
                            answering = True
                            answering_index = int(msg) - 1
                            break
                    except Exception as e:
                        print(e)
                        if "invalid literal for int() with base 10: '[club193110116|@change___it] " in str(e):
                            break

                    if answering and 'Показать вопросы' not in msg:
                        attach = []
                        if current_message['attachments'] is not None:
                            for i in range(len(current_message['attachments'])):
                                attach.append(current_message['attachments'][i])

                        message = msg.split('[club193110116|@change___it] ')[-1]

                        answer(0, msg, [attach])
                        del questions[0]

                    for index in range(len(questions) - 1):
                        q = f'\n\nБеседа: {get_chat_name_by_id(questions[index]["chat_id"])["items"][0]["chat_settings"]["title"]}' \
                            f'\nИмя: {questions[index]["username"]}\nВопрос:\n"{questions[index]["text"]}"\n\n'
                        if q not in questions_list:
                            questions_list.append(q)

                    if 'Показать вопросы' in msg:
                        if len(questions_list) == 0:
                            sender(1, 'Вопросов пока нет😊', kb=menu_keyboard)
                        else:
                            question_phrase = ''
                            for words in questions_list:
                                question_phrase += words
                            sender(1, 'Список вопросов:' + question_phrase,
                                   kb=inline_keyboard(len(questions_list)).get_keyboard())

                # Отправка сообщения, в случае тега бота
                # try:
                if '@change___it' in msg and chat_id == 5:
                    attach = []
                    if current_message['attachments'] is not None:
                        for i in range(len(current_message['attachments'])):
                            attach.append(current_message['attachments'][i])

                    message = msg.split('[club193110116|@change___it] ')[-1]
                    question(user_id, user, message, [attach])

                    add_question(chat_id, user_id, user, message)

                elif '@change___it' in msg and chat_id == 1 and 'Показать вопросы' not in msg:

                    attach = []
                    if current_message['attachments'] is not None:
                        for i in range(len(current_message['attachments'])):
                            attach.append(current_message['attachments'][i])

                    message = msg.split('[club193110116|@change___it] ')[-1]

                    answer(0, msg, [attach])
                    del questions[0]

                # except Exception as e:
                #     if 'list index out of range' in str(e):
                #         sender(1, 'Вопросов пока нет😊')

                # Проверка на мат
                if chat_id != 1 and chat_id != 3:
                    for word in msg.lower().split():
                        for check_word in bad_words:
                            if check_word in word:
                                # Просим исправиться
                                sender(chat_id, f'@id{user_id} ({user["first_name"]} {user["last_name"]}), пожалуйста,'
                                                f' не употребляй ненормативную лексику!☺️')

                                # Получаем название беседы и ID сообщения с нарушением
                                title = chat['items'][0]['chat_settings']['title']
                                bad_message_id = chat['items'][0]['last_message_id']

                                # Отправляем репорт
                                forward_report(3, title, f'@id{user_id} ({user["first_name"]})', bad_message_id)
