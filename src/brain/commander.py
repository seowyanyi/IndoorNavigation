"""
The commander module coordinates all threads and components
"""
from src.communication import queueManager
from src.peripherals import audio, KeyPad
from src.arduinoInterface import serialmod
import routeManager
import src.mapper.mapper as mapper
import pedometer
import time

def start():
    imuQueue = queueManager.IMU_QUEUE
    audioQueue = queueManager.AUDIO_QUEUE
    pedometerQueue = queueManager.PEDOMETER_QUEUE
    keypadQueue = queueManager.KEYPAD_QUEUE

    # Thread 1
    audio_thread = audio.AudioDispatcherThread(
        threadName='audio Dispatcher', audioQueue=audioQueue)
    audio_thread.daemon = True
    audio_thread.start()

    precomputedData = mapper.init_mapper(audioQueue)

    # Thread 2
    pedometer_thread = pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue, pedometerQueue=pedometerQueue,
        keypressQueue=keypadQueue, audioQueue=audioQueue)
    pedometer_thread.daemon = True
    pedometer_thread.start()

    # Thread 3
    route_manager_thread = routeManager.RouteManagerThread(
        threadName='route Manager', pedometerQueue=pedometerQueue, audioQueue=audioQueue,
        precomputedCheckpointData=precomputedData
    )
    route_manager_thread.daemon = True
    route_manager_thread.start()

    # Thread 4
    sensor_thread = serialmod.SensorManagerThread(
        threadName='sensor Manager', imuQueue=imuQueue)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Thread 5
    #kp_thread = KeyPad.KeypadThread(threadName='keypad', keypressQueue=keypadQueue)
    #kp_thread.daemon = True
    #kp_thread.start()

    while True:
        time.sleep(1000)