# -*- coding: utf-8 -*-
import strings
import python_ruz
from datetime import datetime, timedelta
from config import default_timezone
from users.states_machine.basic_state import BasicState
from users.user_states import tags
from telegram import InlineKeyboardMarkup
import logging

logger = logging.getLogger('start_procedure.GET_EMAIL')


class GetEmail(BasicState):
    tag = tags.GET_EMAIL

    def __init__(self, user):
        super().__init__(user)
        self.email_exists = None
        self.menu_message_id = None

    def enter(self, edit_message_id=None, email_exists=False):
        self.email_exists = email_exists
        if edit_message_id is not None:
            self.user.edit_message(edit_message_id,
                                   strings.enter_email_message,
                                   disable_web_page_preview=True)
        else:
            self.user.send_message(strings.enter_email_message,
                                   disable_web_page_preview=True)

    def exit(self):
        pass

    def remove_keyboard(self):
        return self.user.remove_keyboard(self.menu_message_id)

    def check_email_with_message(self, email, message_len, message_text, edit_message_id=None,
                                 **kwargs):
        logger.debug('Checking Email {} for user {}'.format(email, self.user.user_id))
        assert isinstance(message_len, int)
        sending_message = strings.email_checking_message.format(message_text)
        if edit_message_id is None:
            msg = self.user.send_message(sending_message, **kwargs)
            msg_id = msg.message_id
        else:
            self.user.edit_message(edit_message_id, sending_message, **kwargs)
            msg_id = edit_message_id

        res = python_ruz.person_lessons(datetime.now(default_timezone),
                                        datetime.now(default_timezone) + timedelta(days=message_len - 1),
                                        email)
        return len(res) > 0, msg_id

    def update(self, bot, update):
        email = update.message.text.strip().lower()
        keyboard_for_back_to_menu = None if not self.email_exists else InlineKeyboardMarkup(
            strings.get_email_back_keyboard)
        if self.user.check_email_correct(email):
            test_res = False
            message_id = None
            try:
                for message_len, message_text in strings.email_checking_dates:
                    test_res, message_id = self.check_email_with_message(email,
                                                                         message_len, message_text,
                                                                         message_id,
                                                                         reply_keyboard=keyboard_for_back_to_menu)
                    if test_res:
                        break
                else:
                    self.user.send_message(strings.no_timetable.format(email))
            except python_ruz.utilities.NoEmailOrTimeout:
                self.user.send_message(strings.no_email_error.format(email))
            if test_res:
                assert message_id is not None
                self.user.email = email
                self.user.edit_message(message_id, strings.email_correct_message)
                return BasicState.create_transition(tags.MAIN, invoke=True)
        else:
            self.user.send_message(strings.wrong_email_message, disable_web_page_preview=True)

    def update_callback(self, bot, update):
        pass
