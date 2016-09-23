# -*- coding: utf-8 -*-
import strings
from telegram import InlineKeyboardMarkup
from users.states_machine.basic_state import BasicState
from .. import tags
import logging

logger = logging.getLogger('start_procedure.INIT')


class StartEnter(BasicState):
    tag = tags.START_ENTER

    def __init__(self, user):
        super().__init__(user)
        self.menu_message = None

    def enter_message(self):
        logger.debug('Sending hello message for {}'.format(self.user.user_id))
        if self.menu_message is not None:
            self.user.remove_keyboard(self.menu_message)
        msg = self.user.send_message(text=strings.start_enter_message,
                                     reply_markup=InlineKeyboardMarkup(strings.start_enter_keyboard))
        self.menu_message = msg.message_id

    def enter(self):
        self.menu_message = None

    def exit(self):
        if self.menu_message is not None:
            self.user.remove_keyboard(self.menu_message)
            self.menu_message = None

    def update(self, bot, update):
        self.enter_message()

    def update_callback(self, bot, update):
        if update.callback_query.data == strings.continue_inline_tag:
            return BasicState.create_transition(tags.GET_EMAIL, edit_message_id=self.menu_message)
