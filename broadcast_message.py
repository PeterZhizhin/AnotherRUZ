from telegram import Bot
from telegram.error import BadRequest, Unauthorized

import access_token
from database import Databases

broadcast = "Всем привет! Бот был переписан с нуля и теперь выглядит более опрятно и так" \
            " как должен выглядеть любой бот в 2016.\n" \
            "Скоро планируется добавить ещё возможность просматривать свободные аудитории," \
            " которая должна сделать жизнь во ВШЭ чуточку проще.\n" \
            "Планировалось добавить расписание электричек и автобусов до Дубков для общажников, " \
            "хотелось бы узнать о целесообразности такой вещи в этом боте.\n" \
            "Если есть ошибки, если бот упал, если хочется поговорить за жизнь и всё такое, то пишите мне на @PeterZhizhin\n"
with_mail = "Ваша почта {} была сохранена.\nСпасибо."
no_mail = "Вы не указали почту, попробуйте сделать это сейчас, ведь интерфейс теперь и правда понятный!\nСпасибо."

broadcast_with_mail = broadcast + with_mail
broadcast_no_mail = broadcast + no_mail

already_sent_to = {
    93894659,
    553838,
    1374125,
    1480753,
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
        except Unauthorized:
            wrong_count += 1
            print(user_id, 'not correct')
    print(wrong_count)


if __name__ == "__main__":
    main()
