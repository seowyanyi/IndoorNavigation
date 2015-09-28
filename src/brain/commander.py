"""
The commander module coordinates all threads and components
"""
from src.communication import queueManager
from src.communication import feedbackDispatcher
from src.arduinoInterface import serialmod
import routeManager
import obstacleDetector
import src.mapper.mapper as mapper
import pedometer

def start():
    leftSonarQueue = queueManager.LEFT_SONAR_QUEUE
    rightSonarQueue = queueManager.RIGHT_SONAR_QUEUE
    middleSonarQueue = queueManager.MIDDLE_SONAR_QUEUE
    imuQueue = queueManager.IMU_QUEUE
    audioQueue = queueManager.AUDIO_QUEUE
    hapticQueue = queueManager.HAPTIC_QUEUE

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
    # obstacleDetector.ObstacleDetectorThread(
    #     threadName='obstacleDetector', delaySeconds=1, middleSonarQueue=middleSonarQueue,
    #     leftSonarQueue=leftSonarQueue, rightSonarQueue=rightSonarQueue, audioQueue=audioQueue,
    #     hapticQueue=hapticQueue).start()

    # Thread 4
    # feedbackDispatcher.AudioDispatcherThread(
    #     threadName='audioDispatcher', delaySeconds=1, audioQueue=audioQueue).start()

   # Thread 5
   #  feedbackDispatcher.HapticDispatcherThread(
   #      threadName='hapticDispatcher', delaySeconds=1, hapticQueue=hapticQueue).start()