"""
Gets type of step an bearing after each step from pedometer
Keeps track, and saves to disk, the current location in the following format:
 - building, level,
 - start and end nodes of current edge
 - distance to next node
 - current bearing

 Notifies the user (through audioQueue) when he is approaching the next checkpoint.
"""
import threading
import pedometer
import time
import numpy as np
import Queue

# Audio commands
TURN_X_DEG_CW = 'Turn {} degrees clockwise' 
TURN_X_DEG_ACW = 'Turn {} degrees anti clockwise'
GOOD_TO_GO = 'Good to go. {} steps to next'
DESTINATION_REACHED = 'Destination reached'
CHECKPOINT_REACHED = 'Checkpoint {} reached'
COUNTDOWN_X_LEFT = '{} left'
WALK_X_DEG_LEFT = 'Walk {} degrees left'
WALK_X_DEG_RIGHT = 'Walk {} degrees right'
CURRENT_CHECKPOINT = 'Current checkpoint {}. {}'

# Constants
CM_PER_STEP = 60.5
ACCEPTABLE_BEARING_ERROR_STAIONARY = 20 # degrees
ACCEPTABLE_BEARING_ERROR_MOVING = 15 # degrees
NUM_STEPS_BEFORE_CORRECTING = 5
COUNTDOWN_FROM_X_STEPS = 4
RADIANS_PER_DEGREE = 0.0174533
SECS_BEFORE_GOOD_TO_GO_REPEAT = 25

def guide_user_to_next_checkpoint(target_bearing, pedometerQueue, audioQueue, threshold):
    prev_angle = 0
    while True:
        data = pedometerQueue.get(True)
        if data['type'] != pedometer.Step.AT_REST:
            continue
        if abs(target_bearing - data['actual_bearing']) < threshold:
            break
        if data['actual_bearing'] != prev_angle:
            prev_angle = data['actual_bearing']
            guide_user(data['actual_bearing'], target_bearing, audioQueue)
            time.sleep(8)
            pedometerQueue.queue.clear()

def guide_user(actual_bearing, target_bearing, audioQueue):
    difference = int(target_bearing - actual_bearing)
    # check how much to turn, and whether CW or CCW
    print 'guiding user. target: {} deg, actual: {} deg'.format(target_bearing, actual_bearing)
    if 0 < difference <= 180:
        audioQueue.put(TURN_X_DEG_CW.format(difference))
    elif difference > 180:
        difference = 360 - difference
        audioQueue.put(TURN_X_DEG_ACW.format(difference))
    elif -180 <= difference < 0 :
        audioQueue.put(TURN_X_DEG_ACW.format(abs(difference)))
    else:
        difference += 360
        audioQueue.put(TURN_X_DEG_CW.format(difference))

def guide_user_while_walking(actual_bearing, target_bearing, audioQueue):
    difference = int(target_bearing - actual_bearing)
    # check how much to turn, and whether CW or CCW
    print 'guiding user. target: {} deg, actual: {} deg'.format(target_bearing, actual_bearing)
    if 0 < difference <= 180:
        audioQueue.put(WALK_X_DEG_RIGHT.format(difference))
    elif difference > 180:
        difference = 360 - difference
        audioQueue.put(WALK_X_DEG_LEFT.format(difference))
    elif -180 <= difference < 0 :
        audioQueue.put(WALK_X_DEG_LEFT.format(abs(difference)))
    else:
        difference += 360
        audioQueue.put(WALK_X_DEG_RIGHT.format(difference))



class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, pedometerQueue, audioQueue, keypressQueue, precomputedCheckpointData):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.pedometerQueue = pedometerQueue
        self.audioQueue = audioQueue
        self.precomputedCheckpointData = precomputedCheckpointData
        self.keypressQueue = keypressQueue

    def run(self):
        print  'Starting {} thread'.format(self.threadName)
        start_managing_routes(self.pedometerQueue, self.audioQueue, self.keypressQueue, self.precomputedCheckpointData)
        print 'Exited {} thread'.format(self.threadName)

def start_managing_routes(pedometerQueue, audioQueue, keypressQueue, precomputedCheckpointData):
    curr_index = -1
    reached_checkpoint = True
    distance_to_next = 0
    steps = 0
    steps_between_checkpoints = 0
    good_to_go_time = int(time.time())
    recent_bearings = []

    # Get rid of unnecessary stuff in queue to speed up processing.
    pedometerQueue.queue.clear()

    while True:
        if reached_checkpoint:
            curr_index += 1
            reached_checkpoint = False
            steps_between_checkpoints = 0
            curr_node = precomputedCheckpointData[curr_index]
            currNodeId = curr_node['curr_checkpoint']
            curr_node_name = curr_node['curr_node_name']
            if curr_index == len(precomputedCheckpointData) - 1:
                #reached destination
                audioQueue.put(CURRENT_CHECKPOINT.format(currNodeId, curr_node_name))
                audioQueue.put(DESTINATION_REACHED)
                break
            else:
                audioQueue.put(CURRENT_CHECKPOINT.format(currNodeId, curr_node_name))
                if curr_node['is_linkage']:
                    audioQueue.put('linking to next map')
                    reached_checkpoint = True
                    continue
                distance_to_next = curr_node['distance_to_next']
                bearing_to_next = curr_node['bearing_to_next']
                checkpoint = curr_node['next_checkpoint']

                if curr_node['is_staircase']:
                    distance_to_next = 6 * CM_PER_STEP # 6 steps per flight of stairs
                    audioQueue.put(GOOD_TO_GO.format(round(distance_to_next/CM_PER_STEP,1)))
                else :
                    guide_user_to_next_checkpoint(bearing_to_next, pedometerQueue, audioQueue, ACCEPTABLE_BEARING_ERROR_STAIONARY)
                    audioQueue.put(GOOD_TO_GO.format(round(distance_to_next/CM_PER_STEP,1)))
                    pedometerQueue.queue.clear()
                    good_to_go_time = int(time.time())
                    print 'Distance to node {}: {} cm Bearing to {}: {} deg'.format(checkpoint, distance_to_next, checkpoint, bearing_to_next)

        else:
            try:
                keypress = keypressQueue.get(False)
                if keypress == 'overshot':
                    audioQueue.put('Overshot. Calibrating to next checkpoint')
                    reached_checkpoint = True
                    continue
                elif keypress == 'undershot':
                    audioQueue.put('Undershot. Pedometer paused for 8 seconds')
                    time.sleep(8)
                    audioQueue.put('Pedometer restarted')
                    pedometerQueue.queue.clear()

            except Queue.Empty:
                pass
            data = pedometerQueue.get(True)

            if data['type'] == pedometer.Step.FORWARD:
                recent_bearings.append(data['actual_bearing'])
                bearing_error = np.average(recent_bearings) - bearing_to_next
                steps += 1
                steps_between_checkpoints += 1
                distance_to_next -= CM_PER_STEP

                print 'Step taken. Heading: {} deg.'.format(data['actual_bearing'])
                # start counting down a few steps before reaching next checkpoint
                if 0 < distance_to_next <= COUNTDOWN_FROM_X_STEPS * CM_PER_STEP:
                    audioQueue.put(COUNTDOWN_X_LEFT.format(round(distance_to_next / CM_PER_STEP,1)))

                if steps == NUM_STEPS_BEFORE_CORRECTING and distance_to_next > 0:
                    steps = 0
                    if abs(bearing_error) > ACCEPTABLE_BEARING_ERROR_MOVING:
                        guide_user_while_walking(np.average(recent_bearings), bearing_to_next, audioQueue)
                        recent_bearings = []
            elif data['type'] == pedometer.Step.AT_REST:
                if steps_between_checkpoints == 0 and int(time.time()) - good_to_go_time >= SECS_BEFORE_GOOD_TO_GO_REPEAT:
                    # Case 1: User still at checkpoint. Maybe he missed the command to go
                    audioQueue.put('Current checkpoint is {}'.format(precomputedCheckpointData[curr_index]['curr_checkpoint']))
                    audioQueue.put(GOOD_TO_GO.format(round(distance_to_next/CM_PER_STEP,1)))
                    good_to_go_time = int(time.time())
            if distance_to_next <= 0:
                checkpoint = precomputedCheckpointData[curr_index]['next_checkpoint']
                reached_checkpoint = True
                audioQueue.put(CHECKPOINT_REACHED.format(checkpoint))

            if pedometerQueue.qsize() > 1:
                print 'pedo queue size: {}'.format(pedometerQueue.qsize())

