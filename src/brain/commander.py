"""
The commander module coordinates all threads and components
"""
from src.communication import queueManager
from src.peripherals import audio, KeyPad
from src.arduinoInterface import serialmod
import routeManager
import src.mapper.mapper as mapper
import pedometer


def start():
    imuQueue = queueManager.IMU_QUEUE
    audioQueue = queueManager.AUDIO_QUEUE
    pedometerQueue = queueManager.PEDOMETER_QUEUE
    keypadQueue = queueManager.KEYPAD_QUEUE

    # Thread 1
    audio.AudioDispatcherThread(
        threadName='audio Dispatcher', audioQueue=audioQueue).start()


    precomputedData = mapper.init_mapper(audioQueue)

    # Thread 2
    pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue, pedometerQueue=pedometerQueue,
        keypressQueue=keypadQueue, audioQueue=audioQueue).start()

    
    # Thread 3
    routeManager.RouteManagerThread(
        threadName='route Manager', pedometerQueue=pedometerQueue, audioQueue=audioQueue,
        precomputedCheckpointData=precomputedData
    ).start()
    
    # Thread 4
    serialmod.SensorManagerThread(
        threadName='sensor Manager', imuQueue=imuQueue).start()

    # Thread 5
    #KeyPad.KeypadThread(threadName='keypad', keypressQueue=keypadQueue).start()
