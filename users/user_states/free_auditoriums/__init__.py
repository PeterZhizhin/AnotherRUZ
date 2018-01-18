import asyncio
import functools
import json
from datetime import datetime

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext.dispatcher import run_async

import python_ruz
from python_ruz import ruz_config
import strings
from users.states_machine.basic_state import BasicState
from users.user_states import tags

import logging

import traceback

logger = logging.getLogger(tags.FREE_AUDITORIUMS)


class FreeAuditoriums(BasicState):
    tag = tags.FREE_AUDITORIUMS
    event_loop = asyncio.get_event_loop()

    def __init__(self, user):
        super().__init__(user)
        self.building = None
        self.date = None
        self.free_auditoriums = None
        self.got_auditoriums_callback = None

    @staticmethod
    def get_pairs_buttons():
        pairs = ruz_config.pairs
        all_buttons = []
        for pair_no, pair in enumerate(pairs, 1):
            all_buttons.append(InlineKeyboardButton(
                strings.free_auditoriums_pair_format.format(
                    pair_no,
                    pair[0].strftime(strings.time_format),
                    pair[1].strftime(strings.time_format),
                ),
                callback_data=json.dumps({'type': 'pair', 'no': pair_no})
            ))
        return all_buttons

    @staticmethod
    def get_pairs_keyboard():
        all_buttons = FreeAuditoriums.get_pairs_buttons()
        back_keyboard = InlineKeyboardButton(strings.back,
                                             callback_data=json.dumps({'type': 'back'})
                                             )

        total_keyboard = list()
        last_row = list()
        for button in all_buttons:
            last_row.append(button)
            if len(last_row) == 2:
                total_keyboard.append(last_row)
                last_row = list()
        if len(last_row) > 0:
            total_keyboard.append(last_row)

        total_keyboard.append([back_keyboard])
        return total_keyboard

    def main_message(self, invoke=False):
        self.user.send_or_edit_message(
            strings.free_auditoriums_main_message.format(
                    strings.format_date(self.date),
                    strings.get_weekday_name(self.date),
                    self.building.building_address
            ),
            invoke=invoke,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(self.get_pairs_keyboard()))

    @staticmethod
    def get_go_to_pairs_choose():
        return InlineKeyboardMarkup(
            strings.get_inline_keyboard(
                [[
                    (
                        strings.go_to_pairs_choose_keyboard_message,
                        json.dumps({'type': 'go_to_pairs'})
                    )
                ]]
            )
        )

    def show_auditoriums(self, pair_no):
        if self.free_auditoriums is None:
            self.got_auditoriums_callback = functools.partial(self.show_auditoriums, pair_no)
            self.user.send_or_edit_message(
                strings.getting_free_auditoriums,
                invoke=False,
                reply_markup=self.get_go_to_pairs_choose()
            )
        else:
            try:
                pairs_list = [auditorium_name
                              for auditorium_name, pairs_availability
                              in self.free_auditoriums.items()
                              if pairs_availability[pair_no - 1]]
                pairs_list.sort()
                pairs_list_str = ', '.join(map(str, pairs_list))
                self.user.send_or_edit_message(
                    strings.free_auditoriums_list_format.format(strings.format_date(self.date),
                                                                strings.get_weekday_name(self.date),
                                                                self.building.building_address,
                                                                pair_no,
                                                                pairs_list_str),
                    invoke=False,
                    reply_markup=self.get_go_to_pairs_choose(),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except:
                self.user.send_or_edit_message(strings.error_during_getting_schedule,
                                               invoke=True)
                logger.error('Error while getting free auditoriums {} {} {}'.format(
                    self.date,
                    self.building.building_oid,
                    repr(self.free_auditoriums)),
                )
                return BasicState.create_transition(tags.MAIN, invoke=True)

    @run_async
    def get_free_auditoriums(self, date, building_id):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.free_auditoriums = python_ruz.get_free_auditoriums(date, building_id)
        if self.got_auditoriums_callback:
            self.got_auditoriums_callback()

    def enter(self, building_id: int, date: datetime):
        self.got_auditoriums_callback = None
        self.free_auditoriums = None
        self.date = date
        self.building = python_ruz.get_building_by_id(building_id)
        self.get_free_auditoriums(date, building_id)
        self.main_message()

    def exit(self):
        self.date = None
        self.building = None
        self.free_auditoriums = None
        self.got_auditoriums_callback = None

    def update(self, bot, update):
        self.main_message(invoke=True)

    def update_callback(self, bot, update):
        try:
            res = json.loads(update.callback_query.data)
        except json.JSONDecodeError:
            return
        try:
            query_type = res['type']
            if query_type == 'pair':
                pair_no = res['no']
                if 1 <= pair_no <= len(ruz_config.pairs):
                    # self.user.bot.answer_callback_query(callback_query_id=update.callback_query.id)
                    return self.show_auditoriums(pair_no)
            elif query_type == 'back':
                # self.user.bot.answer_callback_query(callback_query_id=update.callback_query.id)
                return BasicState.create_transition(tags.MAIN,
                                                    send_keyboard=False, invoke=False,
                                                    go_date=self.date)
            elif query_type == 'go_to_pairs':
                self.got_auditoriums_callback = None
                self.main_message(invoke=False)
        except KeyError:
            return
