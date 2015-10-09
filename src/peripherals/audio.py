import pygame

#----------------------------------------------------------------------------------------------------------
# The audio files should be converted to and used as .ogg files for maximum quality and reliability.
#----------------------------------------------------------------------------------------------------------
#ASK_FOR_STARTING_BUILDING = file
#ASK_FOR_STARTING_LEVEL = file
#ASK_FOR_STARTING_NODE = file
#ASK_FOR_DESTINATION_BUILDING = file
#ASK_FOR_DESTINATION_LEVEL = file
#ASK_FOR_DESTINATION_NODE = file
#CONFIRM_INPUT = file
#TURN_RIGHT = file
#TURN_LEFT = file
#WALK_STRAIGHT = file
#OBSTACLE_STOP = file
file_confirm = "/Users/malavikamenon/IndoorNavigation/src/peripherals/myFile2.ogg"
file = "/Users/malavikamenon/IndoorNavigation/src/peripherals/myFile.ogg"

import threading
import Queue

class AudioCommands:
    """
    The different audio command types available. Remember to increment the range value to
    match the total number of commands
    """
    ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL = range(2)


class AudioDispatcherThread(threading.Thread):
    def __init__(self, threadName, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.audioQueue = audioQueue
    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_audio_processing(self.audioQueue)
        print 'Exited {} thread'.format(self.threadName)

def init_test_queue(queue):
    queue.put(AudioCommands.ASK_FOR_STARTING_BUILDING)
    queue.put(AudioCommands.ASK_FOR_STARTING_LEVEL)

def start_audio_processing(audioQueue):
    while True:
        data = audioQueue.get(True)
        if data == AudioCommands.ASK_FOR_STARTING_BUILDING:
            # output the relevant audio
            pass
        elif data == AudioCommands.ASK_FOR_STARTING_BUILDING:
            # output the relevant audio
            pass

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
    notification = Notification(file, file, file, file, file, file, file_confirm)
    return notification

def Initialize_Direction():
    direction = Direction(file, file, file, file)
    return direction

def output_Notif(notificationType, input):
    pygame.mixer.init()
    pygame.mixer.music.load(notificationType)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

if __name__ == '__main__':
    # run python audio.py to test
    # In the actual program, commander.py will be responsible for starting the audio thread
    test_queue = Queue.Queue()
    init_test_queue(test_queue) # producer
    start_audio_processing(test_queue) # consumer