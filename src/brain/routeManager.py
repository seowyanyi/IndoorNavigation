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
import time

# Audio commands
TURN_X_DEG_CW = 'Turn {} degrees clockwise'
TURN_X_DEG_ACW = 'Turn {} degrees anti clockwise'
GOOD_TO_GO = 'Good to go. {} steps to next checkpoint'
DESTINATION_REACHED = 'Destination reached'
CHECKPOINT_REACHED = 'Checkpoint {} reached'
DISTANCE_LEFT_METERS = '{} meters left'
DISTANCE_LEFT_STEPS = '{} steps left'
PEDOMETER_PAUSED_SECS = 'Pedometer paused. 8. 7. 6. 5. 4. 3. 2. 1'
PEDOMETER_RESTARTED = 'Pedometer restarted'

# Constants
CM_PER_STEP = 71.75
ACCEPTABLE_BEARING_ERROR_STAIONARY = 20 # degrees
ACCEPTABLE_BEARING_ERROR_MOVING = 15 # degrees
NUM_STEPS_BEFORE_CORRECTING = 3
COUNTDOWN_X_STEPS_LEFT = 4
PEDOMETER_PAUSE_SECONDS = 8
CHECK_AT_REST_INVERVAL = 9

def guide_user_to_next_checkpoint(target_bearing, pedometerQueue, audioQueue, threshold):
    data = pedometerQueue.get(True)
    while True:
        if data['type'] != pedometer.Step.AT_REST:
            pedometerQueue.queue.clear()
            data = pedometerQueue.get(True)
            continue
        if abs(target_bearing - data['actual_bearing']) < threshold:
            break
        guide_user(data['actual_bearing'], target_bearing, audioQueue)
        time.sleep(10)
        pedometerQueue.queue.clear()
        data = pedometerQueue.get(True)

def guide_user(actual_bearing, target_bearing, audioQueue):
    difference = target_bearing - actual_bearing
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
    difference = target_bearing - actual_bearing
    # check how much to turn, and whether CW or CCW
    print 'guiding user. target: {} deg, actual: {} deg'.format(target_bearing, actual_bearing)
    if 0 < difference <= 180:
        audioQueue.put('walk slightly right')
    elif difference > 180:
        audioQueue.put('walk slightly left')
    elif -180 <= difference < 0 :
        audioQueue.put('walk slightly left')
    else:
        audioQueue.put('walk slightly right')


class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, pedometerQueue, audioQueue, precomputedCheckpointData):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.pedometerQueue = pedometerQueue
        self.audioQueue = audioQueue
        self.precomputedCheckpointData = precomputedCheckpointData

    def run(self):
        print  'Starting {} thread'.format(self.threadName)
        start_managing_routes(self.pedometerQueue, self.audioQueue, self.precomputedCheckpointData)
        print 'Exited {} thread'.format(self.threadName)

def start_managing_routes(pedometerQueue, audioQueue, precomputedCheckpointData):
    print 'start managing routes'
    curr_index = -1
    reached_checkpoint = True
    distance_to_next = 0
    steps = 0
    steps_between_checkpoints = 0

    prev_time= int(time.time())

    # pausing step counting to avoid obstacles
    pause_step_counting = False
    pedometer_pause_time = int(time.time())

    while True:
        if reached_checkpoint:
            curr_index += 1
            reached_checkpoint = False
            steps_between_checkpoints = 0

            if curr_index == len(precomputedCheckpointData):
                #reached destination
                audioQueue.put(DESTINATION_REACHED)
                break
            else:
                distance_to_next = precomputedCheckpointData[curr_index]['distance_to_next']
                bearing_to_next = precomputedCheckpointData[curr_index]['bearing_to_next']
                checkpoint = precomputedCheckpointData[curr_index]['next_checkpoint']
                currNodeId = precomputedCheckpointData[curr_index]['curr_checkpoint']
                print 'Current checkpoint: {}'.format(currNodeId)
                audioQueue.put('Current checkpoint is {}'.format(currNodeId))
                guide_user_to_next_checkpoint(bearing_to_next, pedometerQueue, audioQueue, ACCEPTABLE_BEARING_ERROR_STAIONARY)
                audioQueue.put(GOOD_TO_GO.format(round(distance_to_next/CM_PER_STEP,1)))
                print 'Distance to node {}: {} cm Bearing to {}: {} deg'.format(checkpoint, distance_to_next, checkpoint, bearing_to_next)

        else:
            data = pedometerQueue.get(True)

            if data['type'] == pedometer.Step.FORWARD and not pause_step_counting:
                prev_time = int(time.time())
                steps += 1
                steps_between_checkpoints += 1
                distance_to_next -= CM_PER_STEP
                if steps == NUM_STEPS_BEFORE_CORRECTING:
                    steps = 0
                    if abs(bearing_to_next - data['actual_bearing']) > ACCEPTABLE_BEARING_ERROR_MOVING:
                        guide_user_while_walking(data['actual_bearing'], bearing_to_next, audioQueue)

                # start counting down a few steps before reaching next checkpoint
                if 0 < distance_to_next <= COUNTDOWN_X_STEPS_LEFT * CM_PER_STEP:
                    audioQueue.put(DISTANCE_LEFT_STEPS.format(round(distance_to_next / CM_PER_STEP,1)))

            elif data['type'] == pedometer.Step.AT_REST and int(time.time()) - prev_time >= CHECK_AT_REST_INVERVAL:
                prev_time = int(time.time())
                if steps_between_checkpoints == 0:
                    # Case 1: User still at checkpoint. Maybe he missed the command to go
                    audioQueue.put(DISTANCE_LEFT_STEPS.format(round(distance_to_next/CM_PER_STEP,1)))
                elif pause_step_counting and int(time.time()) - pedometer_pause_time > PEDOMETER_PAUSE_SECONDS:
                    # Case 2: User finished avoiding obstacle and is ready to go
                    audioQueue.put(PEDOMETER_RESTARTED + '. ' + DISTANCE_LEFT_STEPS.format(round(distance_to_next/CM_PER_STEP,1)))
                    print 'pedometer restarted'
                    pause_step_counting = False
                elif not pause_step_counting:
                    # Case 3: User stopped in between checkpoints (probably obstacle).
                    # Pause counting of steps
                    audioQueue.put(PEDOMETER_PAUSED_SECS)
                    print 'pedometer paused'
                    pause_step_counting = True
                    pedometer_pause_time = int(time.time())

            if distance_to_next <= 0:
                checkpoint = precomputedCheckpointData[curr_index]['next_checkpoint']
                reached_checkpoint = True
                audioQueue.put(CHECKPOINT_REACHED.format(checkpoint))
