import Queue

IMU_QUEUE = Queue.Queue()       # IMUData
AUDIO_QUEUE = Queue.Queue()     # {'type': AudioCommands.SOME_COMMAND, 'data': 60}
PEDOMETER_QUEUE = Queue.Queue() # {'type': Step.SOME_STEP, 'actual_bearing': 120}
KEYPRESS_QUEUE = Queue.Queue()    # overshot / undershot

class Sonar:
    LEFT, RIGHT, FRONT, UPPER_SHIN, LOWER_SHIN, GLOVE = range(6)

class IMUData:
    def __init__(self, xAxis, heading, dataRate):
        self.xAxis = xAxis
        self.heading = heading
        self.dataRate = dataRate