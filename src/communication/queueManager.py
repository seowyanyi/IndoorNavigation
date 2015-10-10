import Queue

LEFT_SONAR_QUEUE = Queue.Queue()
RIGHT_SONAR_QUEUE = Queue.Queue()
MIDDLE_SONAR_QUEUE = Queue.Queue()
IMU_QUEUE = Queue.Queue()       # IMUData
AUDIO_QUEUE = Queue.Queue()     # {'type': AudioCommands.SOME_COMMAND, 'data': 60}
PEDOMETER_QUEUE = Queue.Queue() # {'type': Step.SOME_STEP, 'actual_bearing': 120}

class Sonar:
    LEFT, RIGHT, FRONT, UPPER_SHIN, LOWER_SHIN, GLOVE = range(6)

class IMUData:
    def __init__(self, xAxis, yAxis, zAxis, heading):
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis
        self.heading = heading