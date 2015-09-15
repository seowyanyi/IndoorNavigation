"""
from IMU readings, estimate distance traveled
from compass, get direction
with distance and heading, update current location
check how far left
send user feedback if off course
"""
import threading
import time

class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, delaySeconds, imuQueue, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.imuQueue = imuQueue
        self.audioQueue = audioQueue

    def run(self):
        """
        Keep reading from route Manager queues
        Do processing
        Read from storage, update mapper if needed
        Send audio feedback if needed.
        """
        counter = 0
        print 'Starting {} thread'.format(self.threadName)
        while True:
            counter += 1
            data = self.imuQueue.get(True)
            print '{}: received x:{} y:{} z:{} '.format(self.threadName, data.xAxis, data.yAxis, data.zAxis)
            time.sleep(self.delaySeconds)
            if counter % 3 == 0:
                self.audioQueue.put("~~~ turn left ~~~")
            if counter % 2 == 0:
                self.audioQueue.put("~~~ continue walking straight ~~~")
            if counter % 4 == 0:
                self.audioQueue.put("~~~ turn right ~~~")
            if counter > 15:
                break
        print 'Exited {} thread'.format(self.threadName)
