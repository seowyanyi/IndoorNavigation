"""
from IMU readings, estimate distance traveled
from compass, get direction
with distance and heading, update current location
check how far left
send user feedback if off course
"""
import threading

class RouteManagerThread(threading.Thread):
    def __init__(self, threadName, imuQueue, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.imuQueue = imuQueue
        self.audioQueue = audioQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        while True:
            data = self.imuQueue.get(True)
            x = data.xAxis
            y = data.yAxis
            z = data.zAxis

        print 'Exited {} thread'.format(self.threadName)