import planner as planner
import sys
sys.path.insert(0, '/home/pi/IndoorNavigation/src/')
from peripherals import audio
from peripherals import KeyPad

START_BUILDING = 'start_building'
START_LEVEL = 'start_level'
START_NODE = 'start_node'
DESTINATION_BUILDING = 'destination_building'
DESTINATION_LEVEL = 'destination_level'
DESTINATION_NODE = 'destination_node'
KEYPAD_CONFIRM = 1
CONTINUE = '-1'

ASK_FOR_STARTING_BUILDING = 'Please input the starting building'
ASK_FOR_STARTING_LEVEL = 'Please input the starting level'
ASK_FOR_STARTING_NODE = 'Please input the starting node'
ASK_FOR_DESTINATION_BUILDING = 'Please input the destination building'
ASK_FOR_DESTINATION_LEVEL = 'Please input the destination level'
ASK_FOR_DESTINATION_NODE = 'Please input the destination node'
CONFIRM_INPUT = 'Your input is {}. Please confirm your input by pressing 1, to repeat press 2'

def init_mapper(audioQueue):
    locations = get_start_and_end_locations(audioQueue)
    return planner.get_shortest_path(sourceBuilding=locations[START_BUILDING], sourceLevel=locations[START_LEVEL], sourceNodeId=locations[START_NODE], destBuilding=locations[DESTINATION_BUILDING],destLevel=locations[DESTINATION_LEVEL], destNodeId=locations[DESTINATION_NODE])

def get_start_and_end_locations(audioQueue):
    startBuilding = get_starting_building(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        startBuilding = get_starting_building(audioQueue)
    
    startLevel = get_starting_level(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        startLevel = get_starting_level(audioQueue)
    
    startNode = get_starting_nodeID(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        startNode = get_starting_nodeID(audioQueue)
    
    destBuilding = get_destination_building(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        destBuilding = get_destination_building(audioQueue)
    
    destLevel = get_destination_level(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        destLevel = get_destination_level(audioQueue)
    
    destNode = get_destination_nodeID(audioQueue)
    while not is_confirm(keypad.get_user_input()):
        destNode = get_destination_nodeID(audioQueue)

    return {START_BUILDING: startBuilding, START_LEVEL: startLevel, START_NODE: startNode,
        DESTINATION_BUILDING: destBuilding , DESTINATION_LEVEL: destLevel, DESTINATION_NODE: destNode}

def get_destination_building(audioQueue):
    audioQueue.put(ASK_FOR_DESTINATION_BUILDING)
    print "ASK_FOR_DESTINATION_BUILDING"
    return get_input_and_request_confirmation(audioQueue)

def get_destination_level(audioQueue):
    audioQueue.put(ASK_FOR_DESTINATION_LEVEL)
    print "ASK_FOR_DESTINATION_LEVEL"
    return get_input_and_request_confirmation(audioQueue)

def get_destination_nodeID(audioQueue):
    audioQueue.put(ASK_FOR_DESTINATION_NODE)
    print "ASK_FOR_DESTINATION_NODE"
    return get_input_and_request_confirmation(audioQueue)

def get_starting_building(audioQueue):
    audioQueue.put(ASK_FOR_STARTING_BUILDING)
    print "ASK_FOR_STARTING_BUILDING"
    return get_input_and_request_confirmation(audioQueue)

def get_starting_level(audioQueue):
    audioQueue.put(ASK_FOR_STARTING_LEVEL)
    print "ASK_FOR_STARTING_LEVEL"
    return get_input_and_request_confirmation(audioQueue)

def get_starting_nodeID(audioQueue):
    audioQueue.put(ASK_FOR_STARTING_NODE)
    print "ASK_FOR_STARTING_NODE"
    return get_input_and_request_confirmation(audioQueue)

def is_confirm(keypadInput):
    return int(keypadInput) == int(KEYPAD_CONFIRM)

def get_input_and_request_confirmation(audioQueue):
    userInput = keypad.get_user_input()
    audioQueue.put(CONFIRM_INPUT.format(userInput))
    return userInput


def test_audio():
    while True:
        init_mapper()

if __name__ == "__main__":
    test_audio()