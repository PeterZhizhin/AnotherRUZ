# -*- coding: utf-8 -*-
from telegram import TelegramError
from telegram.ext import Updater
from telegram.ext import MessageHandler, CallbackQueryHandler
from users import UserManager
from database import Databases
import config
import logging_settings


logger = logging_settings.init_logging("ruz_main.log")


class Main:
    def __init__(self):
        logger.info("The app has started")
        databases = Databases()
        logger.info("DB initialized")

        self.telegram_updater = Updater(token=config.token)

        self.user_manager = UserManager(databases, self.telegram_updater.bot)
        self.telegram_updater.dispatcher.add_handler(MessageHandler(filters=[],
                                                                    callback=self.message_handler))
        self.telegram_updater.dispatcher.add_handler(CallbackQueryHandler(self.callback_handler))
        self.telegram_updater.dispatcher.add_error_handler(self.telegram_error)

        logger.info("Staring polling")
        self.telegram_updater.start_polling()
        logger.info("Idle")
        self.telegram_updater.idle()

    def message_handler(self, bot, update):
        self.user_manager.get_user(update.message.chat_id).process_message(bot, update)

    def callback_handler(self, bot, update):
        self.user_manager.get_user(update.callback_query.message.chat_id).process_callback(bot, update)

    def telegram_error(self, bot, update, error):
        try:
            raise error
        except TelegramError as details:
            logger.warning('There was a Telegram Error {}'.format(details))


if __name__ == "__main__":
    Main()
