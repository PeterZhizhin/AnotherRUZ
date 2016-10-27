# -*- coding: utf-8 -*-
import strings
from telegram import InlineKeyboardMarkup
from users.states_machine.basic_state import BasicState
from .. import tags

import logging

logger = logging.getLogger('settings.SETTINGS')


class SettingsState(BasicState):
    tag = tags.SETTINGS

    def __init__(self, user):
        super().__init__(user)
        self.menu_message = None

    def enter_message(self, invoke=False):
        logging.debug('Sending settings message for {}'.format(self.user.user_id))
        msg = self.user.send_or_edit_message(text=strings.settings_main.format(self.user.email),
                                             invoke=invoke,
                                             reply_markup=InlineKeyboardMarkup(strings.settings_main_markup))
        if msg is not None:
            self.menu_message = msg.message_id

    def enter(self, invoke=True):
        self.enter_message(invoke=invoke)

    def exit(self):
        if self.menu_message is not None:
            self.user.remove_keyboard(self.menu_message)
            self.menu_message = None

    def update(self, bot, update):
        self.enter_message(invoke=True)

    def update_callback(self, bot, update):
        query_data = update.callback_query.data
        if query_data == strings.change_email_tag:
            return BasicState.create_transition(tags.GET_EMAIL, edit_message_id=self.menu_message,
                                                email_exists=True)
        elif query_data == strings.go_back_tag:
            return BasicState.create_transition(tags.MAIN, send_keyboard=False)
