"""
Computes type of step an bearing after each step
Types of steps:
1. Normal forward step
2. Step sideways left/right (for avoiding obstacles)
3. Turning on the spot
"""
import numpy as np
import Queue
import os
import src.communication.queueManager as qm

test_queue = Queue.Queue()

WINDOW_SIZE = 5
AT_REST_LIMIT = 1
SWING_LIMIT = 2
CM_PER_STEP = 45
#todo: minus ~5 degrees from bearing due to angle of foot

import threading


class Step:
    FORWARD, TURN, AT_REST = range(5)

class PedometerThread(threading.Thread):
    def __init__(self, threadName, imuQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.imuQueue = imuQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_pedometer_processing(self.imuQueue, WINDOW_SIZE, AT_REST_LIMIT, SWING_LIMIT, False)
        print 'Exited {} thread'.format(self.threadName)

def init_test_queue():
    with open('acc_x.txt') as f:
        for line in f:
            test_queue.put(qm.IMUData(int(line), 0, 0))

def start_pedometer_processing(dataQueue, windowSize, atRestLimit, swingLimit, debug):
    steps = 0
    data = []

    swing_count = 0
    at_rest_count = 0
    previouslyAtRest = True

    while True:
        if debug and dataQueue.qsize() <= 1:
            break

        imuData = dataQueue.get(True)
        x = imuData.xAxis
        heading = imuData.heading

        if len(data) > windowSize:
            data.pop(0)

        data.append(x)

        if len(data) < windowSize:
            continue

        if is_downward_swing(data):
            swing_count += 1
        else:
            swing_count = 0

        if is_at_rest(data):
            at_rest_count += 1
        else:
            at_rest_count = 0

        if debug:
            line = get_equation_of_line(data)
            gradient = line[0]
            write_to_gradient_file(gradient)

        # count as at rest
        if at_rest_count > atRestLimit:
            previouslyAtRest = True
            at_rest_count = 0

        if previouslyAtRest and swing_count > swingLimit:
            steps += 1
            print 'NUMBER OF STEPS: {}'.format(steps)
            print 'DISTANCE TRAVELLED: {} cm'.format(steps * CM_PER_STEP)
            print 'CURRENT HEADING: {} degrees\n'.format(heading)

            swing_count = 0
            previouslyAtRest = False
            at_rest_count = 0
            if debug:
                write_to_step_file('1')
        elif debug:
            write_to_step_file('0')

def write_to_gradient_file(data):
    with open("gradient.txt", "a") as myfile:
        myfile.write(str(data) + '\n')

def write_to_step_file(data):
    with open("step.txt", "a") as myfile:
        myfile.write(data + '\n')


def get_equation_of_line(data):
    x = np.arange(0,len(data))
    y = np.array(data)
    return np.polyfit(x,y,1)

def is_downward_swing(data):
    line = get_equation_of_line(data)
    gradient = line[0]
    return gradient < -0.30

def is_at_rest(data):
    line = get_equation_of_line(data)
    gradient = abs(line[0])
    return gradient <= 0.15

def clean_up():
    try:
        os.remove("step.txt")
    except OSError:
        pass
    try:
        os.remove("gradient.txt")
    except OSError:
        pass

if __name__ == "__main__":
    clean_up()
    init_test_queue()
    start_pedometer_processing(test_queue, WINDOW_SIZE, AT_REST_LIMIT, SWING_LIMIT, True)
