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
imuQueue = queueManager.IMU_QUEUE
audioQueue = queueManager.AUDIO_QUEUE
pedometerQueue = queueManager.PEDOMETER_QUEUE

def pedometer_check():
    # check whether pedometer functioning correctly
    audioQueue.put('Take five steps now.')
    steps_taken = 0
    start_time = int(time.time())

    while int(time.time()) - start_time < 40 and steps_taken < 5:
        data = pedometerQueue.get(True)
        if data['type'] == pedometer.Step.FORWARD:
            audioQueue.put('{} step'.format(steps_taken))
            steps_taken += 1

    if steps_taken < 5:
        audioQueue.put('You took less than five steps within the given time')


def start(debug):

    pedometer_thread = pedometer.PedometerThread(
        threadName='pedometer', imuQueue=imuQueue, pedometerQueue=pedometerQueue)
    pedometer_thread.daemon = True
    pedometer_thread.start()


    sensor_thread = serialmod.SensorManagerThread(
        threadName='sensor Manager', imuQueue=imuQueue, audioQueue=audioQueue)
    sensor_thread.daemon = True
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, False)
    time.sleep(1)
    GPIO.output(7, True)
    sensor_thread.start()


    if not debug:
        audio_thread = audio.AudioDispatcherThread(
            threadName='audio Dispatcher', audioQueue=audioQueue)
        audio_thread.daemon = True
        audio_thread.start()

        pedometer_check()

        precomputedData = mapper.init_mapper(audioQueue)
        while not precomputedData:
            print 'map not found'
            audioQueue.put('map not found.')
            precomputedData = mapper.init_mapper(audioQueue)


        route_manager_thread = routeManager.RouteManagerThread(
            threadName='route Manager', pedometerQueue=pedometerQueue, audioQueue=audioQueue,
            precomputedCheckpointData=precomputedData
        )
        route_manager_thread.daemon = True
        route_manager_thread.start()

    while True:
        time.sleep(2000)

if __name__ == "__main__":
    start(True)