"""
The commander module coordinates all threads and components
"""
from src.communication import queueManager
from src.peripherals import audio
from src.arduinoInterface import serialmod
import routeManager
import src.mapper.mapper as mapper
import pedometer

def start():
    
    leftSonarQueue = queueManager.LEFT_SONAR_QUEUE
    rightSonarQueue = queueManager.RIGHT_SONAR_QUEUE
    middleSonarQueue = queueManager.MIDDLE_SONAR_QUEUE
    imuQueue = queueManager.IMU_QUEUE
    audioQueue = queueManager.AUDIO_QUEUE
    pedometerQueue = queueManager.PEDOMETER_QUEUE

    # Thread 1
    audio.AudioDispatcherThread(
        threadName='audio Dispatcher', audioQueue=audioQueue).start()


    precomputedData = mapper.init_mapper(audioQueue)

    # Thread 2
    serialmod.SensorManagerThread(
        threadName='sensor Manager', imuQueue=imuQueue,
        middleSonarQueue=middleSonarQueue, leftSonarQueue=leftSonarQueue,
        rightSonarQueue=rightSonarQueue).start()

    # Thread 3
    pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue, pedometerQueue=pedometerQueue).start()


    # Thread 4
    routeManager.RouteManagerThread(
        threadName='route Manager', pedometerQueue=pedometerQueue, audioQueue=audioQueue,
        precomputedCheckpointData=precomputedData
    ).start()