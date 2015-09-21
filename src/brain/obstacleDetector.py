from src.arduinoInterface import actuators
import threading
import time

class ObstacleDetectorThread(threading.Thread):
    def __init__(self, threadName, delaySeconds, middleSonarQueue,
                 leftSonarQueue, rightSonarQueue, hapticQueue, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.middleSonarQueue = middleSonarQueue
        self.leftSonarQueue = leftSonarQueue
        self.rightSonarQueue = rightSonarQueue
        self.hapticQueue = hapticQueue
        self.audioQueue = audioQueue

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

            if counter % 2 == 0:
                self.hapticQueue.put("buzzz")

            if counter % 3 == 0:
                self.hapticQueue.put("buzzzzzzzzzzzzzzzzz")

            time.sleep(self.delaySeconds)
            if counter > 15:
                break
        print 'Exited {} thread'.format(self.threadName)

