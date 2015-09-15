import planner.RoutePlanning as planner
import src.peripherals.audio as audio
import src.peripherals.keypad as keypad

START_BUILDING = 'start_building'
START_LEVEL = 'start_level'
START_NODE = 'start_node'
DESTINATION_BUILDING = 'destination_building'
DESTINATION_LEVEL = 'destination_level'
DESTINATION_NODE = 'destination_node'
KEYPAD_CONFIRM = '1'

def init_mapper():
    locations = get_start_and_end_locations()
    planner.find_shortest_path(
        sourceBuilding=locations[START_BUILDING], sourceLevel=locations[START_LEVEL],
        sourceNodeId=locations[START_NODE], destBuilding=locations[DESTINATION_BUILDING],
        destLevel=locations[DESTINATION_LEVEL], destNodeId=locations[DESTINATION_NODE])

def get_start_and_end_locations():
    startBuilding = get_starting_building()
    while not is_confirm(keypad.getInput()):
        startBuilding = get_starting_building()

    startLevel = get_starting_level()
    while not is_confirm(keypad.getInput()):
        startLevel = get_starting_level()

    startNode = get_starting_nodeID()
    while not is_confirm(keypad.getInput()):
        startNode = get_starting_nodeID()

    destBuilding = get_destination_building()
    while not is_confirm(keypad.getInput()):
        destBuilding = get_destination_building()

    destLevel = get_destination_level()
    while not is_confirm(keypad.getInput()):
        destLevel = get_destination_level()

    destNode = get_destination_nodeID()
    while not is_confirm(keypad.getInput()):
        destNode = get_destination_nodeID()

    return {START_BUILDING: startBuilding, START_LEVEL: startLevel, START_NODE: startNode,
            DESTINATION_BUILDING: destBuilding , DESTINATION_LEVEL: destLevel, DESTINATION_NODE: destNode}

def get_destination_building():
    audio.output(audio.Notify.ASK_FOR_DESTINATION_BUILDING)
    return get_input_and_request_confirmation()

def get_destination_level():
    audio.output(audio.Notify.ASK_FOR_DESTINATION_LEVEL)
    return get_input_and_request_confirmation()

def get_destination_nodeID():
    audio.output(audio.Notify.ASK_FOR_DESTINATION_NODE)
    return get_input_and_request_confirmation()

def get_starting_building():
    audio.output(audio.Notify.ASK_FOR_STARTING_BUILDING)
    return get_input_and_request_confirmation()

def get_starting_level():
    audio.output(audio.Notify.ASK_FOR_STARTING_LEVEL)
    return get_input_and_request_confirmation()

def get_starting_nodeID():
    audio.output(audio.Notify.ASK_FOR_STARTING_NODE)
    return get_input_and_request_confirmation()

def is_confirm(keypadInput):
    return keypadInput == KEYPAD_CONFIRM

def get_input_and_request_confirmation():
    userInput = keypad.getInput()
    audio.output(audio.Notify.CONFIRM_INPUT, userInput)
    return userInput