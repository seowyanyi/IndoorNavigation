from time import sleep
from matrix_keypad import RPi_GPIO
import threading

class KeypadThread(threading.Thread):
    def __init__(self, threadName, keypressQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.keypressQueue = keypressQueue
    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        start_checking_for_keypresses(self.keypressQueue)
        print 'Exited {} thread'.format(self.threadName)

def start_checking_for_keypresses(keypressQueue):
    while True:
        keyPad = keypad()
        inp = keyPad.get_user_input()
        if inp == 1 or inp == 4 or inp == 7:
            keypressQueue.put(True)
        elif inp == 3 or inp == 6 or inp == 9:
            keypressQueue.put(False)


class keypad:
    def __init__(self):
        self.kp = RPi_GPIO.keypad(columnCount = 3)

    #Get a single input from the keypad and sleep for a while
    def get_digit(self):
        digit = None
        while digit == None:
            digit = self.kp.getKey()
        sleep(0.5)
        return digit

    #Get a string of inputs from the user
    def get_user_input(self):
        userInput = 0
        digit = self.get_digit()
        while digit != "*" and digit != "#":
            userInput = userInput * 10
            userInput = userInput + digit
            digit = self.get_digit()
        #Reset current user input if user input #
        if digit == "#":
            userInput = self.get_user_input()
        return int(userInput)
