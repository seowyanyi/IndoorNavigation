import Queue

LEFT_SONAR_QUEUE = Queue.Queue()
RIGHT_SONAR_QUEUE = Queue.Queue()
MIDDLE_SONAR_QUEUE = Queue.Queue()
IMU_QUEUE = Queue.Queue()
AUDIO_QUEUE = Queue.Queue()
HAPTIC_QUEUE = Queue.Queue()

class Sonar:
    Left, Right, Front, UpperShin, LowerShin, IMU = range(6)

class IMUData:
    def __init__(self, xAxis, yAxis, zAxis):
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis