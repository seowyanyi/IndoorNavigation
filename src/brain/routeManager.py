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
ACCEPTABLE_BEARING_ERROR_STAIONARY = 4 # degrees
NUM_STEPS_BEFORE_CORRECTING = 3

def guide_user_to_next_checkpoint(target_bearing, pedometerQueue, audioQueue, threshold):
    data = pedometerQueue.get(True)
    while abs(target_bearing - data['actual_bearing']) > threshold:
        guide_user(data['actual_bearing'], target_bearing, audioQueue)



def guide_user(actual_bearing, target_bearing, audioQueue):
    difference = target_bearing - actual_bearing
    # check how much to turn, and whether CW or CCW
    if 0 < difference <= 180:
        audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CW, 'data': difference})
    elif difference > 180:
        difference = 360 - difference
        audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CCW, 'data': difference})
    elif -180 <= difference < 0 :
        audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CCW, 'data': abs(difference)})
    else:
        difference += 360
        audioQueue.put({'type': audio.AudioCommands.TURN_X_DEGREES_CW, 'data': difference})



class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, pedometerQueue, audioQueue, precomputedCheckpointData):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.pedometerQueue = pedometerQueue
        self.audioQueue = audioQueue
        self.precomputedCheckpointData = precomputedCheckpointData

    def run(self):
        logger.info( 'Starting {} thread'.format(self.threadName))
        start_managing_routes(self.pedometerQueue, self.audioQueue, self.precomputedCheckpointData)
        logger.info('Exited {} thread'.format(self.threadName))

def start_managing_routes(pedometerQueue, audioQueue, precomputedCheckpointData):
    curr_index = 0 # first checkpoint has 0 index
    reached_checkpoint = False
    distance_to_next = precomputedCheckpointData[curr_index]['distance_to_next']
    bearing_to_next = precomputedCheckpointData[curr_index]['bearing_to_next']

    steps = 0

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
                guide_user_to_next_checkpoint(bearing_to_next, pedometerQueue, audioQueue, ACCEPTABLE_BEARING_ERROR_STAIONARY)
                audioQueue.put({'type': audio.AudioCommands.METERS_TO_NEXT, 'data': int(distance_to_next/100)})
                logger.info('Distance to next: {} cm Bearing to next: {} deg'.format(distance_to_next, bearing_to_next))

        else:
            data = pedometerQueue.get(True)

            if data['type'] == pedometer.Step.FORWARD:
                steps += 1
                distance_to_next -= CM_PER_STEP

            if steps == NUM_STEPS_BEFORE_CORRECTING:
                steps = 0
                guide_user(data['actual_bearing'], bearing_to_next, audioQueue)

            if distance_to_next <= 10 * CM_PER_STEP:
                # start counting down 10 steps before reaching next checkpoint
                audioQueue.put({'type': audio.AudioCommands.NUM_STEPS_LEFT,
                                     'data': int(distance_to_next / CM_PER_STEP)})
            if distance_to_next <= 0:
                reached_checkpoint = True
                audioQueue.put({'type': audio.AudioCommands.CHECKPOINT_REACHED})