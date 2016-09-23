# -*- coding: utf-8 -*-
from .meta_class import StateMetaClass
from users.user_states import *


class StateMachine:
    def __init__(self, user, initial_state_tag):
        self.states = {class_tag: class_constructor(user)
                       for class_tag, class_constructor
                       in StateMetaClass.states.items()}
        self.state = self.states[initial_state_tag]

    def change_state(self, params, silent=False):
        if params is None:
            return
        tag = params[0]
        args = params[1]
        if not silent:
            self.state.exit()
        self.state = self.states[tag]
        if not silent:
            self.state.enter(**args)

    def process_message(self, bot, update):
        res = self.state.update(bot, update)
        self.change_state(res)

    def process_inline_req(self, bot, update):
        self.state.update_inline_req(bot, update)

    def process_inline_ans(self, bot, update):
        self.state.update_inline_ans(bot, update)

    def process_callback(self, bot, update):
        res = self.state.update_callback(bot, update)
        self.change_state(res)
