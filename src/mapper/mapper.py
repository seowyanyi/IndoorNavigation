import planner as planner
import sys
sys.path.insert(0, '/Users/malavikamenon/IndoorNavigation/src/')
from peripherals import audio
from peripherals import keypad

notify = audio.Initialize_Notif()

START_BUILDING = 'start_building'
START_LEVEL = 'start_level'
START_NODE = 'start_node'
DESTINATION_BUILDING = 'destination_building'
DESTINATION_LEVEL = 'destination_level'
DESTINATION_NODE = 'destination_node'
KEYPAD_CONFIRM = 1
CONTINUE = '-1'

def init_mapper():
    locations = get_start_and_end_locations()
    print locations
    path = planner.get_shortest_path(sourceBuilding=locations[START_BUILDING], sourceLevel=locations[START_LEVEL], sourceNodeId=locations[START_NODE], destBuilding=locations[DESTINATION_BUILDING],destLevel=locations[DESTINATION_LEVEL], destNodeId=locations[DESTINATION_NODE])
    print path

def get_start_and_end_locations():
    startBuilding = get_starting_building()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        startBuilding = get_starting_building()
    
    startLevel = get_starting_level()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        startLevel = get_starting_level()
    
    startNode = get_starting_nodeID()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        startNode = get_starting_nodeID()
    
    destBuilding = get_destination_building()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        destBuilding = get_destination_building()
    
    destLevel = get_destination_level()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        destLevel = get_destination_level()
    
    destNode = get_destination_nodeID()
    while not is_confirm(keypad.getInput()):
        print "is not confirmed"
        destNode = get_destination_nodeID()

    return {START_BUILDING: startBuilding, START_LEVEL: startLevel, START_NODE: startNode,
        DESTINATION_BUILDING: destBuilding , DESTINATION_LEVEL: destLevel, DESTINATION_NODE: destNode}

def get_destination_building():
    audio.output_Notif(notify.ASK_FOR_DESTINATION_BUILDING, CONTINUE)
    print "ASK_FOR_DESTINATION_BUILDING"
    return get_input_and_request_confirmation()

def get_destination_level():
    audio.output_Notif(notify.ASK_FOR_DESTINATION_LEVEL, CONTINUE)
    print "ASK_FOR_DESTINATION_LEVEL"
    return get_input_and_request_confirmation()

def get_destination_nodeID():
    audio.output_Notif(notify.ASK_FOR_DESTINATION_NODE, CONTINUE)
    print "ASK_FOR_DESTINATION_NODE"
    return get_input_and_request_confirmation()

def get_starting_building():
    audio.output_Notif(notify.ASK_FOR_STARTING_BUILDING, CONTINUE)
    print "ASK_FOR_STARTING_BUILDING"
    return get_input_and_request_confirmation()

def get_starting_level():
    audio.output_Notif(notify.ASK_FOR_STARTING_LEVEL, CONTINUE)
    print "ASK_FOR_STARTING_LEVEL"
    return get_input_and_request_confirmation()

def get_starting_nodeID():
    audio.output_Notif(notify.ASK_FOR_STARTING_NODE, CONTINUE)
    print "ASK_FOR_STARTING_NODE"
    return get_input_and_request_confirmation()

def is_confirm(keypadInput):
    return int(keypadInput) == int(KEYPAD_CONFIRM)

def get_input_and_request_confirmation():
    userInput = raw_input('input: ')
    audio.output_Notif(notify.CONFIRM_INPUT, userInput)
    return userInput


def test_audio():
    while True:
        init_mapper()

if __name__ == "__main__":
    test_audio()