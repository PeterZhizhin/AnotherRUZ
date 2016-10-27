# -*- coding: utf-8 -*-
import access_token
import logging
from pytz import timezone
token = access_token.token

file_log_level = logging.DEBUG
console_log_level = logging.DEBUG
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

default_timezone = timezone('Europe/Moscow')

timeout_for_pooling = 3600
retries_on_error = 5
