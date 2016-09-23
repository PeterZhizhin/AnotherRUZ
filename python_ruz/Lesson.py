# -*- coding: utf-8 -*-
from typing import List, Iterable, Dict

import asyncio

import aiohttp
from requests.exceptions import Timeout, ConnectTimeout, ReadTimeout
import requests

from datetime import datetime, date, timedelta
from . import utilities
from . import Auditorium, Lecturer, Building

import logging

logger = logging.getLogger('python_ruz.Lesson')


class Lesson:
    def __init__(self, lesson_dict: dict):
        lesson_date = utilities.format_date(lesson_dict['date']).date()
        lesson_begin_time = utilities.format_time(lesson_dict['beginLesson']).time()
        lesson_end_time = utilities.format_time(lesson_dict['endLesson']).time()
        self.begin_lesson = datetime.combine(lesson_date, lesson_begin_time)
        self.end_lesson = datetime.combine(lesson_date, lesson_end_time)

        self.kind_of_work = lesson_dict['kindOfWork']
        self.discipline = lesson_dict['discipline']
        self.building = Building.Building(building_address=lesson_dict['building'])
        self.auditorium = Auditorium.Auditorium(lesson_dict['auditoriumOid'], lesson_dict['auditorium'])
        self.lecturer = Lecturer.Lecturer(lesson_dict['lecturerOid'], lesson_dict['lecturer'])

    def format_lesson(self, lesson_format: str, date_format: str, time_format: str):
        """
        Форматирование данного занятия в заданном формате
        :param lesson_format: Строка формата урока для метода str.format. Доступные поля:
            begin_lesson_time Время начала занятия в формате параметра time_format
            end_lesson_time Время конца занятия в формате параметра time_format
            lesson_date Дата занятия в формате параметра date_format
            kind_of_work Наименование вида работы (практическое занятие, лекция и т.д.)
            discipline Наименование дисциплины
            building Адрес или аббревиатура здания занятия
            auditorium_oid ID аудитории
            auditorium_number Номер аудитории
            lecturer ФИО преподавателя
            lecturer_oid ID преподавателя
        :param date_format: Формат времени в формате python datetime для datetime.strptime
        :param time_format: Формат времени в формате python datetime для datetime.strptime
        """
        begin_time_str = self.begin_lesson.strftime(time_format)
        end_time_str = self.end_lesson.strftime(time_format)
        date_str = self.begin_lesson.strftime(date_format)
        return lesson_format.format(begin_lesson_time=begin_time_str,
                                    end_lesson_time=end_time_str,
                                    lesson_date=date_str,
                                    kind_of_work=self.kind_of_work,
                                    discipline=self.discipline,
                                    building=self.building.building_address,
                                    auditorium_oid=self.auditorium.auditorium_oid,
                                    auditorium_number=self.auditorium.number,
                                    lecturer=self.lecturer.name,
                                    lecturer_oid=self.lecturer.lecturer_oid)


def _convert_lessons(lessons_dict_list: List[dict]) -> List[Lesson]:
    lessons_class_list = []
    for lesson in lessons_dict_list:
        lessons_class_list.append(Lesson(lesson))
    return lessons_class_list


def person_lessons(from_date: date, to_date: date, email: str) -> List[Lesson]:
    logger.debug('Getting lessons for {} from {} to {}'.format(email, from_date, to_date))
    if from_date > to_date or (to_date - from_date).days >= 180:
        raise utilities.WrongTimePeriod

    if email.endswith('@edu.hse.ru'):
        receiver_type = 0
    elif email.endswith('@hse.ru'):
        receiver_type = 1
    else:
        raise utilities.WrongEmailException

    try:
        result = requests.get(utilities.base_url.format('personlessons'),
                              params={
                                  'fromDate': from_date.strftime(utilities.date_format),
                                  'toDate': to_date.strftime(utilities.date_format),
                                  'email': email,
                                  'receiverType': receiver_type
                              },
                              timeout=utilities.default_timeout)
    except (Timeout, ConnectTimeout, ReadTimeout):
        raise utilities.NoEmailOrTimeout
    if result.status_code == 400:
        raise utilities.NoEmailOrTimeout

    if result.content == b'':
        return []

    return _convert_lessons(result.json())


def auditorium_lessons(from_date: date, to_date: date, auditorium_id: int) -> List[Lesson]:
    if from_date > to_date or (to_date - from_date).days >= 180:
        raise utilities.WrongTimePeriod
    receiver_type = 2
    result = requests.get(utilities.base_url.format('personlessons'),
                          params={
                              'fromDate': from_date.strftime(utilities.date_format),
                              'toDate': to_date.strftime(utilities.date_format),
                              'receiverType': receiver_type,
                              'auditoriumOid': auditorium_id
                          })
    return _convert_lessons(result.json())


async def async_auditoriums_lessons(from_date: date, to_date: date,
                                    auditorium_ids: Iterable[int]) -> Dict[int, List[Lesson]]:
    if from_date > to_date or (to_date - from_date).days >= 180:
        raise utilities.WrongTimePeriod
    receiver_type = 2
    auditorium_ids = list(auditorium_ids)
    async with aiohttp.ClientSession() as session:
        futures = [asyncio.ensure_future(utilities.async_get(session, utilities.base_url.format('personlessons'),
                                                             params={
                                                                 'fromDate': from_date.strftime(utilities.date_format),
                                                                 'toDate': to_date.strftime(utilities.date_format),
                                                                 'receiverType': receiver_type,
                                                                 'auditoriumOid': auditorium_id
                                                             })) for auditorium_id in auditorium_ids]
        results = await asyncio.gather(*futures)
        return {auditorium_ids[i]: _convert_lessons(results[i]) for i in range(len(auditorium_ids))}


def auditoriums_lessons(from_date: date, to_date: date, auditorium_ids: Iterable[int]) -> Dict[int, List[Lesson]]:
    future = asyncio.ensure_future(async_auditoriums_lessons(from_date, to_date, auditorium_ids))
    asyncio.get_event_loop().run_until_complete(future)
    return future.result()


def auditoriums_lessons_in_building(from_date: date, to_date: date, building_id=None) -> Dict[str, List[Lesson]]:
    auditorium_ids_numbers_dict = {i.auditorium_oid: i.number for i in Auditorium.auditoriums(building_id)}

    result = auditoriums_lessons(from_date, to_date, auditorium_ids_numbers_dict.keys())
    for elem in list(result.keys()):
        result[auditorium_ids_numbers_dict[elem]] = result.pop(elem)
    return result


def get_free_auditoriums(request_date: date,
                         building_id: int = None,
                         remove_intervals_smaller_than: timedelta = None):
    if remove_intervals_smaller_than is None:
        remove_intervals_smaller_than = timedelta()
    lessons_start_datetime = datetime.combine(request_date, utilities.lessons_start)
    lessons_end_datetime = datetime.combine(request_date, utilities.lessons_end)
    last_empty_lesson = (lessons_end_datetime, lessons_end_datetime)
    full_day_free = (lessons_start_datetime, lessons_end_datetime)

    auditoriums_timetable = auditoriums_lessons_in_building(request_date, request_date, building_id)
    auditorium_availability = dict()
    for auditorium_no, auditorium_info in auditoriums_timetable.items():
        assert all(i.begin_lesson.date() == request_date for i in auditorium_info)
        intervals = [(i.begin_lesson, i.end_lesson) for i in auditorium_info]
        intervals.sort()
        intervals = utilities.unique_sorted_list(intervals)
        auditorium_free = []
        if intervals:
            intervals.append(last_empty_lesson)
            current_time = lessons_start_datetime
            for interval in intervals:
                new_end = interval[0]
                if new_end != current_time:
                    auditorium_free.append((current_time, new_end))
                current_time = interval[1]
        else:
            auditorium_free.append(full_day_free)
        auditorium_availability[auditorium_no] = [i for i in auditorium_free if
                                                  i[1] - i[0] > remove_intervals_smaller_than]
    return auditorium_availability
