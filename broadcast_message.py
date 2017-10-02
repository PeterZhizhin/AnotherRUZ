from telegram import Bot
from telegram.error import BadRequest, Unauthorized

import access_token
from database import Databases

broadcast = """Мне сообщают о проблемах с ботом. К сожалению, по какой-то причине, на любой запрос РУЗ отвечает 404 (страница не найдена). А при попытке открыть ruz.hse.ru - ничего не получется, страница висит."""
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
