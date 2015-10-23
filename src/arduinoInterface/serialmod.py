import sprotapi as sprotapi
import sprotpkt as sprotpkt
# import serialmod as serialmod
import threading
import communication.queueManager as qm # Don't take this out
import Queue
import RPi.GPIO as GPIO
import timeit
import time

DATA_SIZE = 16
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004
SERIALMOD_BAUDRATE = 115200

ACC_X_DATA_FILE = "acc_x.txt"
ACC_Y_DATA_FILE = "acc_y.txt"
ACC_Z_DATA_FILE = "acc_z.txt"
COMPASS_DATA_FILE = "compass.txt"
DATA_RATE_FILE = "data_rate.txt"
WRITE_FILE_BUFFER = 35 # only write to file every x data points for efficiency


sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=SERIALMOD_BAUDRATE)

canPrint = False
iterationCount = 0
sonar1Data = 0      # Left Sonar
sonar2Data = 0      # Right Sonar
sonar3Data = 0      # Middle Sonar
compassData = 0
footsensData = 0
LIMIT_DATA_RATE = 2
PKT_READ_TIMEOUT_SECS = 0.5 # this should be <= timeout set in sprotcfg.py
RESET_TIMEOUT_SECS = 8 # minimum time between resets
#
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(21,GPIO.OUT)
# GPIO.output(21,GPIO.HIGH)
# time.sleep(0.05)
# GPIO.output(21,GPIO.LOW)
ARDUINO_ALIVE = 'Arduino alive. Good to go'
ARDUINO_DIED = 'Stop now. Arduino died'

class SensorManagerThread(threading.Thread):
    def __init__(self, threadName, imuQueue, audioQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.imuQueue = imuQueue
        self.audioQueue = audioQueue

    def run(self):
        print 'Starting {} thread'.format(self.threadName)
        read_packet(LIMIT_DATA_RATE, self.imuQueue, self.audioQueue)
        print 'Exited {} thread'.format(self.threadName)


def append_list_to_file(data, filename):
    with open(filename, 'a') as myfile:
        for item in data:
            if not isinstance(item, str):
                item = str(item)
            myfile.write(item + '\n')


# Extract sonar data from generic packet
def convertPacketToSonarData(strpkt):
    sonarData = { strpkt[0] : strpkt[2:5] }
    return sonarData

# Strips trailing zeroes if required
def removeNullChars(str):
    maxIndex = 7
    for i in range(maxIndex):
        if(str[i].isdigit() or str[i] == '.'):
            maxIndex = i

    return str[0:maxIndex+1]

def restart_arduino():
    GPIO.output(7, False)
    time.sleep(1)
    GPIO.output(7, True)

def read_packet(limit, imuQueue, audioQueue):
    counter = 1
    prev_time = timeit.default_timer()
    # buffer for writing to files
    acc_x_buffer = []
    time_diff_buffer = []
    compass_buffer = []

    # restarting arduino when data stops
    prev_reset = timeit.default_timer()
    is_arduino_dead = False

    while True :

        # Read a packet
        pkt_read_start = timeit.default_timer()
        pkt = sprotapi.SPROTReceive()
        pkt_read_end = timeit.default_timer()
        if pkt_read_end - pkt_read_start >= PKT_READ_TIMEOUT_SECS and \
                                pkt_read_end - prev_reset >= RESET_TIMEOUT_SECS :
            is_arduino_dead = True
            audioQueue.put(ARDUINO_DIED)
            restart_arduino()
            prev_reset = timeit.default_timer()

        try :
                # Check for error
                if not isinstance(pkt, sprotpkt.SPROTPacket):
                    #print "recv error"
                    sprotapi.SPROTFlush()
                    pass
                    # time.sleep(2)
                    # GPIO.output(21,True)
                    # time.sleep(0.05)
                    # GPIO.output(21,False)
                else :
                    #print "DATA="
                    #print pkt.data
                    strpkt = pkt.data.decode("ascii")

                    if is_arduino_dead:
                        is_arduino_dead = False
                        audioQueue.put(ARDUINO_ALIVE)

                    if strpkt[0] == b'a':
                        data = strpkt.split(":")
                        xyz = data[1].split(",")

                        if counter == 1:
                            #print "c:" + xyz[0] + " x:" + xyz[1]
                            heading = int(xyz[0])
                            #print 'arduino heading: {}'.format(heading)
                            x = int(xyz[1])

                            curr_time = timeit.default_timer()
                            diff = curr_time - prev_time
                            imuQueue.put(qm.IMUData(xAxis=x, heading=heading, dataRate=diff))
                            prev_time = curr_time

                            # if len(acc_x_buffer) == WRITE_FILE_BUFFER:
                            #     append_list_to_file(acc_x_buffer, ACC_X_DATA_FILE)
                            #     acc_x_buffer = []
                            #
                            # if len(time_diff_buffer) == WRITE_FILE_BUFFER:
                            #     append_list_to_file(time_diff_buffer, DATA_RATE_FILE)
                            #     time_diff_buffer = []
                            #
                            # if len(compass_buffer) == WRITE_FILE_BUFFER:
                            #     append_list_to_file(compass_buffer, COMPASS_DATA_FILE)
                            #     compass_buffer = []
                            #
                            # acc_x_buffer.append(x)
                            # time_diff_buffer.append(diff)
                            # compass_buffer.append(heading)

                        if counter == limit:
                            counter = 0
                        counter += 1

                    elif (strpkt[0] == b'2') :
                        sonar2Data = convertPacketToSonarData(strpkt)
                    elif (strpkt[0] == b'3') :
                        sonar3Data = convertPacketToSonarData(strpkt)
                    elif (strpkt[0] == b'C') :
                        compassData = strpkt[2:5]
                                   
        except:
            sprotapi.SPROTClose()
            sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=SERIALMOD_BAUDRATE)

if __name__ == "__main__":
    read_packet(LIMIT_DATA_RATE, Queue.Queue())
