from telegram import Bot
from telegram.error import BadRequest, Unauthorized

import access_token
from database import Databases

broadcast = """Дорогие пользователи, 

Бот вновь работает после весьма продолжительного периода неработоспособности. Вы можете пользоваться им, как и раньше.

Я бы хотел дополнительно рассказать, что случилось. Из-за борьбы Роскомнадзора с Telegram, в какой-то момент мой бот был выключен самим телеграмом на непродолжительный период времени. Потом бот включили обратно, но он продолжать работу не мог, требовалась ручная перезагрузка. Я не поднял бота сразу же, так как в середине апреля мне поставили диагноз, связанный с отслоением сетчатки глаза. Ситуация весьма серьёзная, и мне уже сделали операцию, скоро запланирована ещё одна. Дело затягивается и мне даже придётся уйти в академ.

Дополнительно к тому, мой сервер, с помощью которого работает бот, был забанен Роскомнадзором (в рамках тотальной зачистки Интернета для борьбы с Telegram), я потерял к нему доступ и ничего не мог починить. Чтобы всё исправить, мне нужно было настроить vpn, но из-за болезни это всё растянулось на две недели. 

Также отмечу, что на поддержание работы бота я трачу около 300 рублей в месяц, и если вы чувствуете в себе желание поддержать меня в этой непростой ситуации, а также помочь мне с арендой сервера, то вы можете перевести денег способами, указанными в конце сообщения. Любым деньгам буду рад: продлю аренду сервера на год работы, может быть куплю себе вкусняшку, если что-то останется (а может и вложу в какую-то из операций, если останется много).

Ну и можете писать мне пожелания скорейшего выздоровления, я буду признателен: @PeterZhizhin

Большое всем спасибо :3

Карточка Тинькофф: 5536 9137 6810 0360 (перевод без комиссии на https://www.tinkoff.ru/cardtocard/)
Карта Райффайзен: 4627 2914 7007 5250
Карта Cбербанк (карта моей девушки Закировой Ксении, 1% комиссия): 4276 0600 6185 7994 или по номеру телефона +7 999 978 62 92
Ещё можете переводить деньги сюда: https://yasobe.ru/na/hse_ruz_bot (я уплачу где-то 2-5% комиссии Яндексу).
"""
no_mail = "Вы не указали почту, попробуйте сделать это сейчас, ведь интерфейс теперь и правда понятный!\nСпасибо."

broadcast_with_mail = broadcast
broadcast_no_mail = broadcast #+ no_mail

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
