# -*- coding: utf-8 -*-
from telegram.error import BadRequest

from .states_machine import StateMachine
from .user_states import tags
import re

hse_email_re = re.compile('[A-Za-z_0-9]+@(edu\.)?hse\.ru')


class User:
    def __init__(self, chat_id, users_db, bot):
        self.users_db = users_db
        self.bot = bot

        self.user_id = chat_id
        user_info = self.users_db.get_user(self.user_id)
        if user_info is None:
            self.users_db.add_user(self.user_id)
            user_info = self.users_db.get_user(self.user_id)
        self._email = user_info.get('email', None)
        self._main_menu_message = user_info.get('main_menu_message', None)

        self.state_machine = StateMachine(self, tags.MAIN if self.email is not None else tags.START_ENTER)

    def send_message(self, text, *args, **kwargs):
        return self.bot.sendMessage(*args, text=text, chat_id=self.user_id, **kwargs)

    def remove_keyboard(self, message_id):
        try:
            return self.bot.editMessageReplyMarkup(chat_id=self.user_id,
                                                   message_id=message_id)
        except BadRequest:
            return

    def edit_message(self, message_id, text, *args, **kwargs):
        return self.bot.editMessageText(*args, chat_id=self.user_id,
                                        message_id=message_id,
                                        text=text,
                                        **kwargs)

    def send_or_edit_message(self, *args, invoke=True, **kwargs):
        if self.main_menu_message is None:
            invoke = True

        if self.main_menu_message is not None and invoke:
            self.remove_keyboard(self.main_menu_message)
            self.main_menu_message = None

        if invoke:
            result = self.send_message(*args, **kwargs)
            self.main_menu_message = result.message_id
            return result
        else:
            return self.edit_message(self.main_menu_message, *args, **kwargs)

    @staticmethod
    def check_email_correct(email):
        return isinstance(email, str) and hse_email_re.match(email)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value
        self.users_db.set_email(self.user_id, value)

    @property
    def main_menu_message(self):
        return self._main_menu_message

    @main_menu_message.setter
    def main_menu_message(self, value):
        self._main_menu_message = value
        self.users_db.set_main_menu_message(self.user_id, value)

    def process_message(self, bot, update):
        self.state_machine.process_message(bot, update)

    def process_callback(self, bot, update):
        self.state_machine.process_callback(bot, update)


class UserManager:
    def __init__(self, databases, bot):
        self.users_dict = dict()
        self.users_db = databases.get_users_db()
        self.bot = bot

    def get_user(self, user_id):
        if user_id not in self.users_dict:
            self.users_dict[user_id] = User(user_id, self.users_db, self.bot)
        return self.users_dict[user_id]
