import planner as planner
import sys
sys.path.insert(0, '/home/pi/IndoorNavigation/src/')
from peripherals import audio
from peripherals import KeyPad

keypad = KeyPad.keypad()

START_BUILDING = 'start_building'
START_LEVEL = 'start_level'
START_NODE = 'start_node'
DESTINATION_BUILDING = 'destination_building'
DESTINATION_LEVEL = 'destination_level'
DESTINATION_NODE = 'destination_node'
KEYPAD_CONFIRM = 1
CONTINUE = '-1'

ASK_FOR_STARTING = 'Input starting building, level and node.'
ASK_FOR_DESTINATION = 'Input ending building, level and node'
CONFIRM_INPUT = 'Your input is building {}, level {}, node {}. Press 1 to confirm'

def init_mapper(audioQueue):
    locations = get_start_and_end_locations(audioQueue)
    print locations
    return planner.get_shortest_path(sourceBuilding=locations[START_BUILDING], sourceLevel=locations[START_LEVEL], sourceNodeId=locations[START_NODE], destBuilding=locations[DESTINATION_BUILDING],destLevel=locations[DESTINATION_LEVEL], destNodeId=locations[DESTINATION_NODE])

def get_start_and_end_locations(audioQueue):
    startLocation = get_starting(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        startLocation = get_starting(audioQueue)

    destLocation = get_destination(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        destLocation = get_destination(audioQueue)

    return {START_BUILDING: startLocation[0], START_LEVEL: startLocation[1], START_NODE: startLocation[2],
        DESTINATION_BUILDING: destLocation[0] , DESTINATION_LEVEL: destLocation[1], DESTINATION_NODE: destLocation[2]}

def get_destination(audioQueue):
    audioQueue.put(ASK_FOR_DESTINATION)
    print "ASK_FOR_DESTINATION"
    return get_input_and_request_confirmation(audioQueue)

def get_starting(audioQueue):
    audioQueue.put(ASK_FOR_STARTING)
    print "ASK_FOR_STARTING"
    return get_input_and_request_confirmation(audioQueue)

def is_confirm(keypadInput):
    return int(keypadInput) == int(KEYPAD_CONFIRM)

def get_input_and_request_confirmation(audioQueue):
    building = keypad.get_user_input()
    level = keypad.get_user_input()
    node = keypad.get_user_input()
    userInput = [building, level, node]
    audioQueue.put(CONFIRM_INPUT.format(building, level, node))
    return userInput