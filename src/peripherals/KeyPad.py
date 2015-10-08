from time import sleep
from matrix_keypad import RPi_GPIO

class KeyPad:
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
        return userInput

    #Run to get and return 2 strings of user input as a list
    def run(self):
        data = []
        userInput = self.get_user_input()
        data.append(userInput)
        userInput = self.get_user_input()
        data.append(data)
        return data
    
if __name__ == "__main__":
    ui = KeyPad()
    data = ui.run()
    print data[0]
    print data[1]
