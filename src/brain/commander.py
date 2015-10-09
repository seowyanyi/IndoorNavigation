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

    # mapper.init_mapper()

    # Thread 1
    serialmod.SensorManagerThread(
        threadName='sensorManager', imuQueue=imuQueue,
        middleSonarQueue=middleSonarQueue, leftSonarQueue=leftSonarQueue,
        rightSonarQueue=rightSonarQueue).start()

    # Thread 2
    pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue).start()

    # Thread 3
    audio.AudioDispatcherThread(
        threadName='audioDispatcher', audioQueue=audioQueue).start()