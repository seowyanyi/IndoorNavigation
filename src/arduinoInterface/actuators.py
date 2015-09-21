class Actuator:
    LEFT, RIGHT, GLOVE = range(3)

class HapticFeedback:
    def __init__(self, strength, actuatorType):
        self.strength = strength
        self.actuatorType = actuatorType