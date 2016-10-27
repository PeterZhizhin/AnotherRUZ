from telegram import Bot
from telegram.error import BadRequest, Unauthorized

import access_token
from database import Databases

broadcast = "Я тут добавил поиск свободных аудиторий. Пока это работает только для тех корпусов, " \
            "где в этот день у вас проходят занятия. " \
            "Для других корпусов не очень понятно, что делать (так как у ВШЭ для РУЗа более 50 корпусов), но," \
            " скорее всего, потом " \
            "сделаю выбор из тех корпусов, в которых у вас не так давно были пары.\n" \
            "И да, в некоторых зданиях аудитории имеют достаточно наркоманские имена. Если " \
            "увидите, то присылайте мне сообщения с такими аудиториями в телеграм @PeterZhizhin," \
            " мы подумаем, что с этим можно сделать. Также пишите, если просто хотите поболтать, можем " \
            "обсудить то, чего боту не хватает.\n"
no_mail = "Вы не указали почту, попробуйте сделать это сейчас, ведь интерфейс теперь и правда понятный!\nСпасибо."

broadcast_with_mail = broadcast
broadcast_no_mail = broadcast + no_mail

already_sent_to = {
}


def main():
    bot = Bot(access_token.token)
    users_collection = Databases().get_users_db().users_collection
    wrong_count = 0
    for user in users_collection.find():
        user_id = user['id']
        if user_id in already_sent_to:
            continue
        try:
            if 'email' not in user or user['email'] is None:
                bot.send_message(user_id, broadcast_no_mail)
                print(user_id)
            else:
                email = user['email']
                bot.send_message(user_id, broadcast_with_mail.format(email))
                print(user_id)
        except BadRequest:
            wrong_count += 1
            print(user_id, 'bad request')
        except Unauthorized:
            wrong_count += 1
            print(user_id, 'not correct')
    print(wrong_count)


if __name__ == "__main__":
    main()
