# -*- coding: utf-8 -*-
from typing import List, Dict
from datetime import date, timedelta, time

from python_ruz import Lesson, Auditorium, Building
from python_ruz import utilities


def auditoriums(building_id=None) -> list:
    return Auditorium.auditoriums(building_id)


def buildings() -> list:
    return Building.buildings()


def get_building_by_id(building_id: int) -> Building:
    return Building.get_building_by_id(building_id)


def person_lessons(from_date: date, to_date: date, email: str) -> List[Lesson.Lesson]:
    return Lesson.person_lessons(from_date, to_date, email)


def auditorium_lessons(from_date: date, to_date: date, auditorium_id: int) -> List[Lesson.Lesson]:
    return Lesson.auditorium_lessons(from_date, to_date, auditorium_id)


def auditoriums_lessons(from_date: date, to_date: date,
                        auditoriums_oids: List[int]) -> Dict[int, List[Lesson.Lesson]]:
    return Lesson.auditoriums_lessons(from_date, to_date, auditoriums_oids)


def auditorium_lessons_in_building(from_date: date, to_date: date,
                                   building_id: int = None) -> Dict[str, List[Lesson.Lesson]]:
    return Lesson.auditoriums_lessons_in_building(from_date, to_date, building_id)


def get_free_auditoriums(date: date, building_id=None):
    return Lesson.get_free_auditoriums(date, building_id)
