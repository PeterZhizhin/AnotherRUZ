# -*- coding: utf-8 -*-
from typing import List

import requests
from datetime import datetime

from python_ruz import ruz_config
from . import utilities

import logging

logger = logging.getLogger('python_ruz.Building')


class Building:
    buildings = None
    last_updated_building = None

    def __init__(self, building_address, building_oid=None, building_full_address=None, building_abbr=None):
        self.building_address = building_address
        self.building_oid = building_oid
        self.building_full_address = building_full_address
        self.building_abbr = building_abbr

    def fill_other_info(self):
        logger.debug('Filling all info about the building for building {}'.format(self.building_address))
        all_buildings = buildings()
        for building in all_buildings:
            if building.building_address == self.building_address:
                self.building_address = building.building_address
                self.building_oid = building.building_oid
                self.building_full_address = building.building_full_address
                self.building_abbr = building.building_abbr
                break


def _get_building_class(raw_building):
    return Building(building_oid=raw_building['buildingOid'],
                    building_abbr=raw_building['abbr'],
                    building_address=raw_building['name'],
                    building_full_address=raw_building['address'])


def refresh_buildings():
    raw_buildings = requests.get(utilities.base_url.format('buildings')).json()
    result = []
    for raw_building in raw_buildings:
        result.append(_get_building_class(raw_building))
    Building.buildings = result
    Building.last_updated_building = datetime.utcnow()


def buildings() -> List[Building]:
    if Building.buildings is None or \
                    datetime.utcnow() >= Building.last_updated_building + ruz_config.buildings_update_time:
        refresh_buildings()
    return Building.buildings


def get_building_by_id(building_id):
    all_buildings = buildings()
    for building in all_buildings:
        if building.building_oid == building_id:
            return building
    return None
