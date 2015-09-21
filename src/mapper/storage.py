import json

CURRENT_LOCATION_FILE_NAME = 'current_location.json' 
KEY_EDGE_START = 'edge_start'
KEY_EDGE_END = 'edge_end'
KEY_LEVEL = 'level'
KEY_BUILDING = 'building'
KEY_DIST_OFF_CENTER = 'dist_off_center'
KEY_DIST_TO_NEXT = 'dist_to_next'

def save_map(map):
    pass

def get_maps():
    pass

def save_path(path):
    pass

def get_path():
    pass

def get_current_location():
    with open(CURRENT_LOCATION_FILE_NAME) as infile:
        data = json.load(infile)
    return data


def set_current_location(currentLocationDic):
    with open(CURRENT_LOCATION_FILE_NAME, 'w') as outfile:
        json.dump(currentLocationDic, outfile)


def update_current_location(edgeStart, edgeEnd, distToNext, distOffCenter):
    with open(CURRENT_LOCATION_FILE_NAME) as infile:
        data = json.load(infile)
    data[KEY_EDGE_START] = edgeStart
    data[KEY_EDGE_END] = edgeEnd
    data[KEY_DIST_TO_NEXT] = distToNext
    data[KEY_DIST_OFF_CENTER] = distOffCenter
    set_current_location(data)


def convert_to_current_location_obj(building, level, edgeStart,
                                    edgeEnd, distToNext, distOffCenter):
    if type(building) is not str:
        raise ValueError('Building name is not a string')

    if type(level) is str:
        level = int(level)
    if type(edgeStart) is str:
        edgeStart = int(edgeStart)
    if type(edgeEnd) is str:
        edgeEnd = int(edgeEnd)
    if type(distToNext) is str:
        distToNext = int(distToNext)
    if type(distOffCenter) is str:
        distOffCenter = int(distOffCenter)

    if distToNext < 0:
        raise ValueError('Distance to next {} is less than 0'.format(distToNext))

    obj = {KEY_BUILDING: building, KEY_LEVEL: level, KEY_EDGE_START: edgeStart, KEY_EDGE_END: edgeEnd,
           KEY_DIST_TO_NEXT: distToNext, KEY_DIST_OFF_CENTER: distOffCenter}
    return obj
