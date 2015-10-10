import pygame

#----------------------------------------------------------------------------------------------------------
# The audio files should be converted to and used as .ogg files for maximum quality and reliability.
#----------------------------------------------------------------------------------------------------------
ASK_FOR_STARTING_BUILDING = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_STARTING_BUILDING.ogg"
ASK_FOR_STARTING_LEVEL = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_STARTING_LEVEL.ogg"
ASK_FOR_STARTING_NODE = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_STARTING_NODE.ogg"
ASK_FOR_DESTINATION_BUILDING = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_DEST_BUILDING.ogg"
ASK_FOR_DESTINATION_LEVEL = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_DEST_LEVEL.ogg"
ASK_FOR_DESTINATION_NODE = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/ASK_FOR_DEST_NODE.ogg"
CONFIRM_INPUT = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/CONFIRM_INPUT.ogg"
TURN_RIGHT = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/TURN_RIGHT.ogg"
TURN_LEFT = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/URN_LEFT.ogg"
WALK_STRAIGHT = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/WALK_STRAIGHT.ogg"
OBSTACLE_STOP = "/Users/malavikamenon/IndoorNavigation/src/peripherals/AudioFiles/STOP_OBSTACLE.ogg"


import threading
import Queue

class AudioCommands:
    """
    The different audio command types available. Remember to increment the range value to
    match the total number of commands
    """
    ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL, TURN_X_DEGREES_CCW, TURN_X_DEGREES_CW,\
        SLIGHT_RIGHT, SLIGHT_LEFT, DESTINATION_REACHED, CHECKPOINT_REACHED, NUM_STEPS_LEFT,\
        METERS_TO_NEXT = range(8)


class AudioDispatcherThread(threading.Thread):
    def __init__(self, threadName, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.audioQueue = audioQueue
    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_audio_processing(self.audioQueue)
        print 'Exited {} thread'.format(self.threadName)

def start_audio_processing(audioQueue):
    while True:
        data = audioQueue.get(True)
        if data['type'] == AudioCommands.ASK_FOR_STARTING_BUILDING:
            # output the relevant audio
            pass
        elif data['type'] == AudioCommands.ASK_FOR_STARTING_BUILDING:
            # output the relevant audio
            pass
        elif data['type'] == AudioCommands.TURN_X_DEGREES_CCW:
            degrees = data['data']
        elif data['type'] == AudioCommands.TURN_X_DEGREES_CW:
            # output the relevant audio
            pass
        elif data['type'] == AudioCommands.SLIGHT_LEFT:
            pass
        elif data['type'] == AudioCommands.SLIGHT_RIGHT:
            # output the relevant audio
            pass
        elif data['type'] == AudioCommands.DESTINATION_REACHED:
            pass
        elif data['type'] == AudioCommands.CHECKPOINT_REACHED:
            pass
        elif data['type'] == AudioCommands.NUM_STEPS_LEFT:
            pass
        elif data['type'] == AudioCommands.METERS_TO_NEXT:
            dist_in_meters = data['data']

class Notification:
    def __init__(self, ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL, ASK_FOR_STARTING_NODE, ASK_FOR_DESTINATION_BUILDING, ASK_FOR_DESTINATION_LEVEL, ASK_FOR_DESTINATION_NODE, CONFIRM_INPUT):
        self.ASK_FOR_STARTING_BUILDING = ASK_FOR_STARTING_BUILDING
        self.ASK_FOR_STARTING_LEVEL = ASK_FOR_STARTING_LEVEL
        self.ASK_FOR_STARTING_NODE = ASK_FOR_STARTING_NODE
        self.ASK_FOR_DESTINATION_BUILDING = ASK_FOR_DESTINATION_BUILDING
        self.ASK_FOR_DESTINATION_LEVEL = ASK_FOR_DESTINATION_LEVEL
        self.ASK_FOR_DESTINATION_NODE = ASK_FOR_DESTINATION_NODE
        self.CONFIRM_INPUT = CONFIRM_INPUT

class Direction:
    def __init__(self, TURN_RIGHT, TURN_LEFT, WALK_STRAIGHT, OBSTACLE_STOP):
        self.TURN_RIGHT = TURN_RIGHT
        self.TURN_LEFT = TURN_LEFT
        self.WALK_STRAIGHT = WALK_STRAIGHT
        self.OBSTACLE_STOP = OBSTACLE_STOP

def Initialize_Notif():
    notification = Notification(ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL, ASK_FOR_STARTING_NODE, ASK_FOR_DESTINATION_BUILDING, ASK_FOR_DESTINATION_LEVEL, ASK_FOR_DESTINATION_NODE, CONFIRM_INPUT)
    return notification

def Initialize_Direction():
    direction = Direction(TURN_RIGHT, TURN_LEFT, WALK_STRAIGHT, OBSTACLE_STOP)
    return direction

def output_Notif(notificationType, input):
    play_audio_Command(notificationType)

def play_audio_Command(notificationType):
    pygame.mixer.init()
    pygame.mixer.music.load(notificationType)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def init_test_queue(queue):
    data1 = {'type': AudioCommands.ASK_FOR_STARTING_BUILDING}
    data2 = {'type': AudioCommands.ASK_FOR_STARTING_LEVEL}
    data3 = {'type': AudioCommands.TURN_X_DEGREES_CCW, 'data': 60} # should output "turn 60 degrees ccw"
    queue.put(data1)
    queue.put(data2)
    queue.put(data3)


if __name__ == '__main__':
    # run python audio.py to test
    # In the actual program, commander.py will be responsible for starting the audio thread
    test_queue = Queue.Queue()
    init_test_queue(test_queue) # producer
    start_audio_processing(test_queue) # consumer