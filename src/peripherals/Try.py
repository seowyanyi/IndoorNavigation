import pyttsx
engine = pyttsx.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)
engine.setProperty('volume', 1.0)

engine.say('Turn 90 degree clockwise')
engine.say('Reach checkpoint')
engine.runAndWait()
