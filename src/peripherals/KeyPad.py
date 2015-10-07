from time import sleep
from matrix_keypad import RPi_GPIO

class KeyPad:
    def __init__(self):
        self.data = []
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

    #Run the user interface to get 2 strings of user input
    def run(self):
        data = self.get_user_input()
        self.data.append(data)
        data = self.get_user_input()
        self.data.append(data)

    #Return the user inputs as a list
    def get_data(self):
        return self.data
    
if __name__ == "__main__":
    ui = KeyPad()
    ui.run()
    data = ui.get_data()
    print data[0]
    print data[1]
