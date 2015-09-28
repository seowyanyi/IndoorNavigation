import numpy as np
import Queue
import os
acc_x_sensor = Queue.Queue()
acc_y_sensor = Queue.Queue()
acc_z_sensor = Queue.Queue()
WINDOW_SIZE = 10
AT_REST_LIMIT = 30
SWING_LIMIT = 5

import threading

class PedometerThread(threading.Thread):
    def __init__(self, threadName, imuQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.imuQueue = imuQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_pedometer_processing(acc_y_sensor, WINDOW_SIZE, AT_REST_LIMIT, SWING_LIMIT)
        print 'Exited {} thread'.format(self.threadName)

def init_test_queue():
    with open('acc_y.txt') as f:
        for line in f:
            acc_y_sensor.put(int(line))

    with open('acc_z.txt') as f:
        for line in f:
            acc_z_sensor.put(int(line))

    with open('acc_x.txt') as f:
        for line in f:
            acc_x_sensor.put(int(line))


def start_pedometer_processing(dataQueue, windowSize, atRestLimit, swingLimit):
    steps = 0
    data = []

    swing_count = 0
    at_rest_count = 0
    previouslyAtRest = True

    while True:
        imuData = dataQueue.get(True)
        x = imuData.xAxis
        y = imuData.yAxis
        z = imuData.zAxis

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

        # line = get_equation_of_line(data)
        # gradient = line[0]
        # write_to_gradient_file(gradient)

        # count as at rest
        if at_rest_count > atRestLimit:
            previouslyAtRest = True
            at_rest_count = 0

        if previouslyAtRest and swing_count > swingLimit:
            steps += 1
            print 'NUMBER OF STEPS: {}'.format(steps)
            swing_count = 0
            previouslyAtRest = False
            at_rest_count = 0
        #     write_to_step_file('1')
        # else:
        #     write_to_step_file('0')

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
    return gradient < -0.35

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
    start_pedometer_processing(acc_y_sensor, WINDOW_SIZE, AT_REST_LIMIT, SWING_LIMIT)
