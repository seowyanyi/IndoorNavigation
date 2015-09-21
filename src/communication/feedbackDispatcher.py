import threading
import time

class AudioDispatcherThread(threading.Thread):
    """
    Dispatches audio feedback
    """
    def __init__(self, threadName, delaySeconds, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.audioQueue = audioQueue

    def run(self):
        counter = 0
        print 'Starting {} thread'.format(self.threadName)
        while True:
            counter += 1
            data = self.audioQueue.get(True)
            print '{}: Sending audio command {} '.format(self.threadName, data)
            time.sleep(self.delaySeconds)
            if counter > 5:
                break
        print 'Exited {} thread'.format(self.threadName)


class HapticDispatcherThread(threading.Thread):
    """
    Dispatches audio feedback
    """
    def __init__(self, threadName, delaySeconds, hapticQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.delaySeconds = delaySeconds
        self.hapticQueue = hapticQueue

    def run(self):
        counter = 0
        print 'Starting {} thread'.format(self.threadName)
        while True:
            counter += 1
            data = self.hapticQueue.get(True)
            print '{}: Sending haptic feedback: {}'.format(self.threadName, data)
            time.sleep(self.delaySeconds)
            if counter > 5:
                break
        print 'Exited {} thread'.format(self.threadName)