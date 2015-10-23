"""
The commander module coordinates all threads and components
"""
from communication import queueManager
from peripherals import audio, KeyPad
from arduinoInterface import serialmod
import routeManager
import mapper.mapper as mapper
import pedometer
import time
import RPi.GPIO as GPIO

def start():
    imuQueue = queueManager.IMU_QUEUE
    audioQueue = queueManager.AUDIO_QUEUE
    pedometerQueue = queueManager.PEDOMETER_QUEUE

    # Thread 1
    audio_thread = audio.AudioDispatcherThread(
        threadName='audio Dispatcher', audioQueue=audioQueue)
    audio_thread.daemon = True
    audio_thread.start()

    precomputedData = mapper.init_mapper(audioQueue)
    while not precomputedData:
        print 'map not found'
        audioQueue.put('map not found.')
        precomputedData = mapper.init_mapper(audioQueue)

    # Thread 2
    pedometer_thread = pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue, pedometerQueue=pedometerQueue)
    pedometer_thread.daemon = True
    pedometer_thread.start()

    # Thread 3
    route_manager_thread = routeManager.RouteManagerThread(
        threadName='route Manager', pedometerQueue=pedometerQueue, audioQueue=audioQueue,
        precomputedCheckpointData=precomputedData
    )
    route_manager_thread.daemon = True
    route_manager_thread.start()

    time.sleep(5) # sleep a few seconds to cater for spinning

    # Thread 4
    sensor_thread = serialmod.SensorManagerThread(
        threadName='sensor Manager', imuQueue=imuQueue, audioQueue=audioQueue)
    sensor_thread.daemon = True
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, False)
    time.sleep(1)
    GPIO.output(7, True)
    sensor_thread.start()

    # Thread 5
    #kp_thread = KeyPad.KeypadThread(threadName='keypad', keypressQueue=keypadQueue)
    #kp_thread.daemon = True
    #kp_thread.start()

    while True:
        time.sleep(1000)
