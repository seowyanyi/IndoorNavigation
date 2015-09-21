import unittest
import os
import json

import src.mapper.storage as storage

CURRENT_LOC_FILE_PATH = 'current_location.json'
TEMP_CURRENT_LOC_FILE_PATH = 'temp_current_location.json'

class CurrentLocationObjectConversion(unittest.TestCase):
    def test_positive(self):
        obj = storage.convert_to_current_location_obj(building='COM3', level='2',
                                                   edgeStart=5, edgeEnd='1', distToNext='0', distOffCenter=30)
        self.assertEquals('COM3', obj['building'])
        self.assertEquals(2, obj['level'])
        self.assertEquals(5, obj['edge_start'])
        self.assertEquals(1, obj['edge_end'])
        self.assertEquals(0, obj['dist_to_next'])
        self.assertEquals(30, obj['dist_off_center'])

    def test_negative_distance(self):
        with self.assertRaises(ValueError):
            storage.convert_to_current_location_obj(building='COM3', level='2',
                                                 edgeStart=5, edgeEnd='1', distToNext='-1', distOffCenter=30)

    def test_non_string_building_name(self):
        with self.assertRaises(ValueError):
            storage.convert_to_current_location_obj(building=999, level='2',
                                                 edgeStart=5, edgeEnd='1', distToNext='-1', distOffCenter=30)


class CurrentLocationGetSetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # backup original location file
        if os.path.isfile(CURRENT_LOC_FILE_PATH):
            os.rename(CURRENT_LOC_FILE_PATH, TEMP_CURRENT_LOC_FILE_PATH)

    @classmethod
    def tearDown(cls):
        # remove any location files created during the test
        if os.path.isfile(CURRENT_LOC_FILE_PATH):
            os.remove(CURRENT_LOC_FILE_PATH)

        # restore original location file
        if os.path.isfile(TEMP_CURRENT_LOC_FILE_PATH):
            os.rename(TEMP_CURRENT_LOC_FILE_PATH, CURRENT_LOC_FILE_PATH)

    def test_set_location(self):
        building = 'test building'
        level = 5
        edgeStart = 8
        edgeEnd = 11
        distToNext = 236
        distOffCenter = 30

        currentLoc = storage.convert_to_current_location_obj(building='test building', level=level,
                                                          edgeStart=edgeStart, edgeEnd=edgeEnd,
                                                          distToNext=distToNext, distOffCenter=distOffCenter)
        storage.set_current_location(currentLoc)

        with open(CURRENT_LOC_FILE_PATH) as infile:
            data = json.load(infile)
        self.assertEquals(edgeStart, data['edge_start'])
        self.assertEquals(edgeEnd, data['edge_end'])
        self.assertEquals(level, data['level'])
        self.assertEquals(building, data['building'])
        self.assertEquals(distToNext, data['dist_to_next'])
        self.assertEquals(distOffCenter, data['dist_off_center'])

    def test_update_location(self):
        currentLoc = storage.convert_to_current_location_obj(building='COM4', level=2,
                                                          edgeStart=5, edgeEnd=1, distToNext=0, distOffCenter=30)
        storage.set_current_location(currentLoc)
        edgeStart = 33
        edgeEnd = 0
        distToNext = 875
        distOffCenter = -29

        storage.update_current_location(edgeStart=edgeStart, edgeEnd=edgeEnd,
                                     distToNext=distToNext, distOffCenter=distOffCenter)

        with open(CURRENT_LOC_FILE_PATH) as infile:
            data = json.load(infile)
        # building and level should not change. The rest should.
        self.assertEquals(2, data['level'])
        self.assertEquals('COM4', data['building'])
        self.assertEquals(edgeStart, data['edge_start'])
        self.assertEquals(edgeEnd, data['edge_end'])
        self.assertEquals(distToNext, data['dist_to_next'])
        self.assertEquals(distOffCenter, data['dist_off_center'])

    def test_get_location(self):
        building = 'COM5'
        level = 7
        edgeStart = 42
        edgeEnd = 43
        distToNext = 100
        distOffCenter = 0

        currentLoc = storage.convert_to_current_location_obj(building=building, level=level,
                                                          edgeStart=edgeStart, edgeEnd=edgeEnd,
                                                          distToNext=distToNext, distOffCenter=distOffCenter)
        storage.set_current_location(currentLoc)
        data = storage.get_current_location()
        self.assertEquals(level, data['level'])
        self.assertEquals(building, data['building'])
        self.assertEquals(edgeStart, data['edge_start'])
        self.assertEquals(edgeEnd, data['edge_end'])
        self.assertEquals(distToNext, data['dist_to_next'])
        self.assertEquals(distOffCenter, data['dist_off_center'])




