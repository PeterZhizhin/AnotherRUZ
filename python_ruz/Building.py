# -*- coding: utf-8 -*-
import requests
from . import utilities


class Building:
    def __init__(self, building_address, building_oid=None, building_full_address=None, building_abbr=None):
        self.building_address = building_address
        self.building_oid = building_oid
        self.building_full_address = building_full_address
        self.building_abbr = building_abbr


def buildings() -> list:
    return requests.get(utilities.base_url.format('buildings')).json()
