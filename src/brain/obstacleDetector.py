import threading
import time

class ObstacleDetectorThread(threading.Thread):
    def __init__(self, threadName, delaySeconds, middleSonarQueue, leftSonarQueue, rightSonarQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.middleSonarQueue = middleSonarQueue
        self.leftSonarQueue = leftSonarQueue
        self.rightSonarQueue = rightSonarQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        counter = 0
        while True:
            counter += 1
            leftSonarData = self.leftSonarQueue.get()
            print '{}: received {} on left sonar'.format(self.threadName, leftSonarData)
            rightSonarData = self.rightSonarQueue.get()
            print '{}: received {} on right sonar'.format(self.threadName, rightSonarData)
            middleSonarData = self.middleSonarQueue.get()
            print '{}: received {} on middle sonar'.format(self.threadName, middleSonarData)
            time.sleep(self.delaySeconds)
            if counter > 15:
                break
        print 'Exited {} thread'.format(self.threadName)

