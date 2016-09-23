# -*- coding: utf-8 -*-
import logging
from .meta_class import StateMetaClass


class NoStateFoundException(Exception):
    pass


class BasicState(metaclass=StateMetaClass):
    tag = 'BASIC'
    logger = logging.getLogger('State')
    logger.setLevel(logging.DEBUG)

    @staticmethod
    def create_transition(new_state_tag, **kwargs):
        if new_state_tag not in StateMetaClass.states:
            raise NoStateFoundException
        return new_state_tag, kwargs

    def __init__(self, user):
        self.user = user

    def enter(self, **kwargs):
        pass

    def update(self, bot, update):
        pass

    def update_inline_req(self, bot, update):
        pass

    def update_inline_ans(self, bot, update):
        pass

    def update_callback(self, bot, update):
        pass

    def exit(self):
        pass
