import pyttsx
import threading
import Queue


WALK_STRAIGHT = 'Walk STRAIGHT'
OBSTACLE_STOP = 'STOP. Obstacle ahead'

# Initialise the pyttsx which is the library used for text to speech conversion
def init_player():
    engine = pyttsx.init()
    engine.setProperty('rate', 140)
    engine.setProperty('volume', 1.0)
    return engine
# -----------------------------------------------------------------------------------------

class Notification:
    def __init__(self, ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL, ASK_FOR_STARTING_NODE, ASK_FOR_DESTINATION_BUILDING, ASK_FOR_DESTINATION_LEVEL, ASK_FOR_DESTINATION_NODE, CHECKPOINT_REACHED, DESTINATION_REACHED, METERS_TO_NEXT, NUM_STEPS_LEFT, CONFIRM_INPUT, TURN_X_DEGREES_CW, TURN_X_DEGREES_CCW, WALK_STRAIGHT, OBSTACLE_STOP):
        self.ASK_FOR_STARTING_BUILDING = ASK_FOR_STARTING_BUILDING
        self.ASK_FOR_STARTING_LEVEL = ASK_FOR_STARTING_LEVEL
        self.ASK_FOR_STARTING_NODE = ASK_FOR_STARTING_NODE
        self.ASK_FOR_DESTINATION_BUILDING = ASK_FOR_DESTINATION_BUILDING
        self.ASK_FOR_DESTINATION_LEVEL = ASK_FOR_DESTINATION_LEVEL
        self.ASK_FOR_DESTINATION_NODE = ASK_FOR_DESTINATION_NODE
        self.CHECKPOINT_REACHED = CHECKPOINT_REACHED
        self.DESTINATION_REACHED = DESTINATION_REACHED
        self.METERS_TO_NEXT = METERS_TO_NEXT
        self.CONFIRM_INPUT = CONFIRM_INPUT
        self.NUM_STEPS_LEFT = NUM_STEPS_LEFT
        self.TURN_X_DEGREES_CW = TURN_X_DEGREES_CW
        self.TURN_X_DEGREES_CCW = TURN_X_DEGREES_CCW
        self.WALK_STRAIGHT = WALK_STRAIGHT
        self.OBSTACLE_STOP = OBSTACLE_STOP

def Initialize_Notif():
    notification = Notification(ASK_FOR_STARTING_BUILDING, ASK_FOR_STARTING_LEVEL, ASK_FOR_STARTING_NODE, ASK_FOR_DESTINATION_BUILDING, ASK_FOR_DESTINATION_LEVEL, ASK_FOR_DESTINATION_NODE, CHECKPOINT_REACHED, DESTINATION_REACHED, METERS_TO_NEXT, NUM_STEPS_LEFT, CONFIRM_INPUT, TURN_X_DEGREES_CW, TURN_X_DEGREES_CCW, WALK_STRAIGHT, OBSTACLE_STOP)
    return notification

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
    engine = init_player();
    while True:
        data = audioQueue.get(True)
        engine.say(ASK_FOR_STARTING_BUILDING)
        engine.runAndWait()

def init_test_queue(queue):
    data1 = {'type': Notif.ASK_FOR_STARTING_BUILDING}
    data2 = {'type': Notif.ASK_FOR_STARTING_LEVEL}
    data3 = {'type': Notif.TURN_X_DEGREES_CCW, 'data': 60} # should output "turn 60 degrees ccw"
    data4 = {'type': Notif.NUM_STEPS_LEFT, 'data': 25} # should output "25 steps to the next checkpoint"
    queue.put(data1)
    queue.put(data2)
    queue.put(data3)
    queue.put(data4)


if __name__ == '__main__':
    # run python audio.py to test
    # In the actual program, commander.py will be responsible for starting the audio thread
    Notif = Initialize_Notif()
    test_queue = Queue.Queue()
    init_test_queue(test_queue) # producer
    start_audio_processing(test_queue) # consumer