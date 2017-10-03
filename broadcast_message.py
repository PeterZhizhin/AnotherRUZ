from telegram import Bot
from telegram.error import BadRequest, Unauthorized

import access_token
from database import Databases

broadcast = "Бот вернулся в работу. В будущем планируется наладить общение с ДИТ, чтобы я знал о переменах в их работе и мог вовремя что-то поправить. Извините за ваши потраченные нервы."
no_mail = "Вы не указали почту, попробуйте сделать это сейчас, ведь интерфейс теперь и правда понятный!\nСпасибо."

broadcast_with_mail = broadcast
broadcast_no_mail = broadcast + no_mail

already_sent_to = set()


def main():
    bot = Bot(access_token.token)
    users_collection = Databases().get_users_db().users_collection
    wrong_count = 0
    for user in users_collection.find():
        user_id = user['id']
        if user_id in already_sent_to:
            continue
        try:
            bot.send_message(user_id, broadcast)
            print(user_id)
        except BadRequest:
            wrong_count += 1
            print(user_id, 'bad request')
        except Unauthorized:
            wrong_count += 1
            print(user_id, 'not correct')
        already_sent_to.add(user_id)
    print(wrong_count)


if __name__ == "__main__":
    main()
