# -*- coding: utf-8 -*-
from typing import List
import requests
from . import utilities, Building


class Auditorium:
    def __init__(self, auditorium_oid, number,
                 building_oid=None, building_address=None,
                 auditorium_type=None):
        self.auditorium_oid = auditorium_oid
        self.number = number

        if building_oid is None:
            self.building = None
        else:
            assert building_address is not None
            self.building = Building.Building(building_address, building_oid)

        self.auditorium_type = auditorium_type

    @staticmethod
    def build_from_dict(auditorium_dict):
        return Auditorium(auditorium_dict['auditoriumOid'],
                          auditorium_dict['number'],
                          auditorium_dict['buildingOid'],
                          auditorium_dict['building'],
                          auditorium_dict['typeOfAuditorium'])


def _convert_auditoriums(auditorium_dict_list: List[dict]) -> List[Auditorium]:
    auditorium_class_list = []
    for auditorium in auditorium_dict_list:
        auditorium_class_list.append(Auditorium.build_from_dict(auditorium))
    return auditorium_class_list


def auditoriums(building_id=None) -> List[Auditorium]:
    if building_id is None:
        params = {}
    else:
        params = {'buildingOid': building_id}
    res = requests.get(utilities.base_url.format('auditoriums'), params=params)
    return _convert_auditoriums(res.json())
