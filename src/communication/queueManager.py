import Queue

IMU_QUEUE = Queue.Queue()       # IMUData
AUDIO_QUEUE = Queue.Queue()     # {'type': AudioCommands.SOME_COMMAND, 'data': 60}
PEDOMETER_QUEUE = Queue.Queue() # {'type': Step.SOME_STEP, 'actual_bearing': 120}
KEYPAD_QUEUE = Queue.Queue()    # true for ready to climb stairs

class Sonar:
    LEFT, RIGHT, FRONT, UPPER_SHIN, LOWER_SHIN, GLOVE = range(6)

class IMUData:
    def __init__(self, xAxis, heading, dataRate):
        self.xAxis = xAxis
        self.heading = heading
        self.dataRate = dataRate