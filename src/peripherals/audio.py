import pyttsx
import threading
import Queue
import time

# Initialise the pyttsx which is the library used for text to speech conversion
def init_player():
    eng = pyttsx.init()
    eng.setProperty('rate', 140)
    eng.setProperty('volume', 1.0)
    return eng
# -----------------------------------------------------------------------------------------


def onEnd(name, completed):
    if completed:
        time.sleep(1)
        engine.endLoop()

engine = init_player()
engine.connect('finished-utterance', onEnd)

class AudioDispatcherThread(threading.Thread):
    def __init__(self, threadName, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.audioQueue = audioQueue
    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_audio_processing(self.audioQueue)
        print 'Exited {} thread'.format(self.threadName)


def start_audio_processing(audioQueue):
    while True:
        data = audioQueue.get(True)
        print 'audio dispatcher thread: {}'.format(data)
        engine.say(data)
        engine.startLoop()


if __name__ == '__main__':
    # run python audio.py to test
    # In the actual program, commander.py will be responsible for starting the audio thread
    test_queue = Queue.Queue()
    start_audio_processing(test_queue) # consumer