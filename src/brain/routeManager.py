"""
Gets type of step an bearing after each step from pedometer
Keeps track, and saves to disk, the current location in the following format:
 - building, level,
 - start and end nodes of current edge
 - distance to next node, distance off center
 - current bearing

 Notifies the user (through audioQueue) when he is approaching the next checkpoint.

"""
import threading
import pedometer
import logging
from src.peripherals import audio

logger = logging.getLogger('routeManager')
logger.setLevel(logging.INFO)
# create file handler
fh = logging.FileHandler('navigation.log')
fh.setLevel(logging.INFO)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

CM_PER_STEP = 45
ACCEPTABLE_BEARING_ERROR = 4 # degrees

def guide_user_to_correct_bearing(target_bearing, pedometerQueue, audioQueue):
    data = pedometerQueue.get(True)
    while abs(target_bearing - data['actual_bearing']) > ACCEPTABLE_BEARING_ERROR:
        difference = target_bearing - data['actual_bearing']
        # check how much to turn, and whether CW or CCW
        if difference > 0:
            audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CCW, 'data': difference})
        else:
            audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CW, 'data': difference})

class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, pedometerQueue, p2pQueue, audioQueue, precomputedCheckpointData):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.pedometerQueue = pedometerQueue
        self.audioQueue = audioQueue
        self.p2pQueue = p2pQueue
        self.precomputedCheckpointData = precomputedCheckpointData

    def run(self):
        logger.info( 'Starting {} thread'.format(self.threadName))
        start_managing_routes(self.pedometerQueue, self.p2pQueue, self.audioQueue, self.precomputedCheckpointData)
        logger.info('Exited {} thread'.format(self.threadName))

def start_managing_routes(pedometerQueue, p2pQueue, audioQueue, precomputedCheckpointData):
    curr_index = 0 # first checkpoint has 0 index
    reached_checkpoint = False
    distance_to_next = precomputedCheckpointData[curr_index]['distance_to_next']
    bearing_to_next = precomputedCheckpointData[curr_index]['bearing_to_next']

    while True:
        if reached_checkpoint:
            curr_index += 1
            reached_checkpoint = False

            if curr_index == len(precomputedCheckpointData) - 1:
                #reached destination
                audioQueue.put({'type': audio.AudioCommands.DESTINATION_REACHED})
                break
            else:
                distance_to_next = precomputedCheckpointData[curr_index]['distance_to_next']
                bearing_to_next = precomputedCheckpointData[curr_index]['bearing_to_next']
                guide_user_to_correct_bearing(bearing_to_next, pedometerQueue, audioQueue)
                audioQueue.put({'type': audio.AudioCommands.METERS_TO_NEXT, 'data': int(distance_to_next/100)})
                logger.info('Distance to next: {} cm Bearing to next: {} deg'.format(distance_to_next, bearing_to_next))

        else:
            data = pedometerQueue.get(True)
            p2pQueue.put({'target_bearing': bearing_to_next, 'actual_bearing': data['actual_bearing']})

            if data['type'] == pedometer.Step.FORWARD:
                distance_to_next -= CM_PER_STEP

            if distance_to_next <= 10 * CM_PER_STEP:
                # start counting down 10 steps before reaching next checkpoint
                audioQueue.put({'type': audio.AudioCommands.NUM_STEPS_LEFT,
                                     'data': int(distance_to_next / CM_PER_STEP)})
            if distance_to_next <= 0:
                reached_checkpoint = True
                audioQueue.put({'type': audio.AudioCommands.CHECKPOINT_REACHED})