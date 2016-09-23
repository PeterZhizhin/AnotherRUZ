# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime, time

import aiohttp

base_url = "http://ruz.hse.ru/RUZService.svc/{}"
date_format = '%Y.%m.%d'
time_format = '%H:%M'
lessons_start = time(hour=9)
lessons_end = time(hour=21)
default_timeout = 4


class WrongEmailException(Exception):
    pass


class NoEmailOrTimeout(Exception):
    pass


class WrongTimePeriod(Exception):
    pass


def format_date(date_str):
    return datetime.strptime(date_str, date_format)


def format_time(time_str):
    return datetime.strptime(time_str, time_format)


async def async_get(session: aiohttp.ClientSession, url: str, **kwargs):
    assert isinstance(session, aiohttp.ClientSession)
    try:
        async with session.get(url, **kwargs) as response:
            return await response.json()
    except aiohttp.ClientResponseError:
        await asyncio.sleep(0.2)
        return await async_get(session, url, **kwargs)


def unique_sorted_list(sorted_list):
    result = []
    last_seen = None
    for element in sorted_list:
        if element != last_seen:
            result.append(element)
            last_seen = element
    return result
