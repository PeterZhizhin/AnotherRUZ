# -*- coding: utf-8 -*-
from .. import tags
from datetime import datetime, timedelta
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.error import BadRequest
from telegram.parsemode import ParseMode
from users.states_machine.basic_state import BasicState
import config
import json
import python_ruz
import strings
import logging

from typing import List
from python_ruz.Lesson import Lesson

logger = logging.getLogger('main_state.MAIN')


class MainState(BasicState):
    tag = tags.MAIN

    def get_today_method(self):
        logging.debug('Sending today for {}'.format(self.user.user_id))
        self.send_menu_message(invoke=True)

    def get_tomorrow_method(self):
        logging.debug('Sending tomorrow for {}'.format(self.user.user_id))
        self.go_date(date=self.get_now() + timedelta(days=1), invoke=True)

    def __init__(self, user):
        super().__init__(user)
        get_today = self.get_today_method
        get_tomorrow = self.get_tomorrow_method
        get_settings = lambda: BasicState.create_transition(tags.SETTINGS, invoke=True)
        self.methods_map = {
            strings.get_today_markup: get_today,
            strings.get_today_cmd: get_today,

            strings.get_tomorrow_markup: get_tomorrow,
            strings.get_tomorrow_cmd: get_tomorrow,

            strings.get_settings_markup: get_settings,
            strings.get_settings_cmd: get_settings,

            strings.get_keyboard: lambda: self.send_keyboard_message(),
        }

    @staticmethod
    def get_now():
        return datetime.now(config.default_timezone)

    def get_timetable_date(self, date):
        assert self.user.email is not None
        return python_ruz.person_lessons(date, date, self.user.email)

    def get_today_timetable(self):
        return self.get_timetable_date(self.get_now())

    def find_nearest_lesson(self):
        assert self.user.email is not None
        today = self.get_now()
        for duration in (7, 31, 6 * 30):
            timetable = python_ruz.person_lessons(today, today + timedelta(days=duration - 1), self.user.email)
            if len(timetable) != 0:
                return timetable[0].begin_lesson
        return None

    @staticmethod
    def format_timetable(timetable: List[Lesson]):
        first_lesson_date = timetable[0].begin_lesson.date()
        first_lesson_building = timetable[0].building.building_address
        if first_lesson_date != MainState.get_now().date():
            start = '*{} ({})*\n_{}_\n'.format(strings.format_date(first_lesson_date),
                                               strings.get_weekday_name(first_lesson_date),
                                               first_lesson_building)
        else:
            start = '*{}*'.format(strings.today_string)
        if len(start) > 0:
            start += '\n'
        return start + strings.division_line.join(i.format_lesson(strings.timetable_base,
                                                                  strings.date_format,
                                                                  strings.time_format) for i in timetable).strip()

    def get_navigation_bar(self, target_date=None):
        if target_date is None:
            target_date = self.get_now()
            today_right = True
        else:
            today_right = target_date.date() == self.get_now().date()

        previous_date = target_date - timedelta(days=1)
        previous_date_button = ('< {}'.format(strings.format_date(previous_date)),
                                strings.go_date_fun(previous_date))
        next_date = target_date + timedelta(days=1)
        next_date_button = ('{} >'.format(strings.format_date(next_date)),
                            strings.go_date_fun(next_date))

        if today_right:
            return strings.get_inline_keyboard([[previous_date_button,
                                                 (strings.refresh_string, json.dumps({'type': 'refresh'},
                                                                                     separators=(',', ':'))),
                                                 next_date_button]])
        else:
            return strings.get_inline_keyboard([[previous_date_button,
                                                 (strings.today_string,
                                                  json.dumps({
                                                      'type': 'GoDate',
                                                      'to': strings.today_string_label,
                                                  })),
                                                 next_date_button]])

    @staticmethod
    def get_refresh_bar():
        return strings.get_inline_keyboard([[(strings.refresh_string, json.dumps({'type': 'refresh'},
                                                                                 separators=(',', ':')))]])

    def send_or_edit_message(self, *args, invoke=True, **kwargs):
        if self.user.main_menu_message is None:
            invoke = True

        if self.user.main_menu_message is not None and invoke:
            self.user.remove_keyboard(self.user.main_menu_message)
            self.user.main_menu_message = None

        if invoke:
            result = self.user.send_message(*args, **kwargs)
            self.user.main_menu_message = result.message_id
            return result
        else:
            return self.user.edit_message(self.user.main_menu_message, *args, **kwargs)

    def send_help_message(self, invoke=True):
        logging.debug('Sending help for {}'.format(self.user.user_id))
        self.send_or_edit_message(strings.help_message,
                                  invoke=invoke,
                                  reply_markup=InlineKeyboardMarkup(strings.help_understand_markup))

    def send_keyboard_message(self):
        logging.debug('Sending keyboard for {}'.format(self.user.user_id))
        self.user.send_message(strings.keyboard_message,
                               reply_markup=ReplyKeyboardMarkup(strings.main_keyboard_markup))

    def send_menu_message(self, invoke=False):
        timetable = self.get_today_timetable()
        if len(timetable) == 0:
            nearest_lesson = self.find_nearest_lesson()
            if nearest_lesson is None:
                self.send_or_edit_message(strings.no_timetable_at_all,
                                          invoke=invoke,
                                          reply_markup=InlineKeyboardMarkup(self.get_refresh_bar()))
            else:
                self.send_or_edit_message(strings.no_timetable_today_fun(nearest_lesson),
                                          invoke=invoke,
                                          reply_markup=InlineKeyboardMarkup(
                                              self.get_navigation_bar() +
                                              strings.no_timetable_keyboard_fun(nearest_lesson)))
        else:
            self.send_or_edit_message(self.format_timetable(timetable),
                                      invoke=invoke,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(self.get_navigation_bar()))

    def go_date(self, date, invoke=False):
        if date.date() == self.get_now().date():
            self.send_menu_message(invoke=invoke)
            return
        try:
            timetable = self.get_timetable_date(date)
        except python_ruz.utilities.WrongTimePeriod:
            self.send_or_edit_message(strings.too_far_error.format(strings.format_date(date)),
                                      invoke=invoke,
                                      reply_markup=InlineKeyboardMarkup(strings.get_inline_keyboard(
                                          [[(strings.today_string,
                                             json.dumps({'type': 'GoDate',
                                                         'to': strings.today_string_label},
                                                        separators=(',', ':')))]]
                                      )))
            return
        if len(timetable) == 0:
            self.send_or_edit_message(strings.no_lessons_at_date.format(strings.format_date(date),
                                                                        strings.get_weekday_name(date)),
                                      invoke=invoke,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(self.get_navigation_bar(date)))
        else:
            self.send_or_edit_message(self.format_timetable(timetable),
                                      invoke=invoke,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(self.get_navigation_bar(date)))

    def enter(self, send_keyboard=True, invoke=True):
        if send_keyboard:
            self.send_keyboard_message()
        self.send_menu_message(invoke=invoke)

    def exit(self):
        pass

    def update(self, bot, update):
        message_text = update.message.text
        if message_text in self.methods_map:
            return self.methods_map[message_text]()
        else:
            self.send_help_message()

    def update_callback(self, bot, update):
        logger.debug('Parsing query for {}'.format(self.user.user_id))
        query_id = update.callback_query.id
        try:
            query_data = json.loads(update.callback_query.data)
        except json.decoder.JSONDecodeError:
            return
        try:
            data_type = query_data['type']
            if data_type == 'refresh':
                logging.debug('Refreshing timetable for {}'.format(self.user.user_id))
                self.user.bot.answer_callback_query(callback_query_id=query_id)
                self.send_menu_message(invoke=False)
            elif data_type == 'GoDate':
                date = query_data['to']
                logging.debug('User {} goes to date {}'.format(self.user.user_id, date))
                self.user.bot.answer_callback_query(callback_query_id=query_id)
                if date == 'today':
                    date = self.get_now()
                else:
                    date = datetime.strptime(date, strings.date_format)
                self.go_date(date)
            elif data_type == strings.confirm_help_type:
                logging.debug('Sending help for {}'.format(self.user.user_id))
                self.user.bot.answer_callback_query(callback_query_id=query_id)
                self.send_menu_message(invoke=False)
            else:
                return
        except KeyError:
            return
