from random import randint
import src.communication.queueManager as queueManager
import threading
import time

class SensorManagerThread(threading.Thread):
    def __init__(self, threadName, delaySeconds, imuQueue, middleSonarQueue, leftSonarQueue, rightSonarQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.imuQueue = imuQueue
        self.middleSonarQueue = middleSonarQueue
        self.leftSonarQueue = leftSonarQueue
        self.rightSonarQueue = rightSonarQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        counter = 0
        while True:
            counter += 1
            imuData = get_data_from_IMU()
            self.imuQueue.put(imuData)
            self.middleSonarQueue.put(get_data_from_sonar())
            self.leftSonarQueue.put(get_data_from_sonar())
            self.rightSonarQueue.put(get_data_from_sonar())
            time.sleep(self.delaySeconds)
            if counter > 18:
                break
        print 'Exited {} thread'.format(self.threadName)

def get_data_from_IMU():
    """
    for testing purposes
    """
    x = randint(0, 1000)
    y = randint(0, 1000)
    z = randint(0, 1000)
    return queueManager.IMUData(xAxis=x, yAxis=y, zAxis=z)

def get_data_from_sonar():
    """
    for testing purposes
    """
    return randint(0, 5000)