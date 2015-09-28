import sprotapi as sprotapi
import sprotpkt as sprotpkt
import serialmod as serialmod
import os
DATA_SIZE = 16
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004
SERIALMOD_BAUDRATE = 115200

ACC_X_DATA_FILE = "acc_x.txt"
ACC_Y_DATA_FILE = "acc_y.txt"
ACC_Z_DATA_FILE = "acc_z.txt"
COMPASS_DATA_FILE = "compass.txt"

# Extract sonar data from generic packet
def convertPacketToSonarData(strpkt):
    sonarData = { strpkt[0] : strpkt[2:5] }
    return sonarData

sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=SERIALMOD_BAUDRATE)

PRINT_EVERY_N_ITER = 10
canPrint = False
iterationCount = 0
sonar1Data = 0      # Left Sonar
sonar2Data = 0      # Right Sonar
sonar3Data = 0      # Middle Sonar
compassData = 0
footsensData = 0

# Strips trailing zeroes if required
def removeNullChars(str):
    maxIndex = 7
    for i in range(maxIndex):
        if(str[i].isdigit() or str[i] == '.'):
            maxIndex = i

    return str[0:maxIndex+1]
    
def read_packet():
    counter = 0
    while True :

        # Read a packet
        pkt = sprotapi.SPROTReceive()

        try :
                # Check for error
                if (not isinstance(pkt, sprotpkt.SPROTPacket)) :
                    print "recv error"
                else :
                    pkt.printPacket()
                    strpkt = pkt.data.decode("ascii")

                    if (strpkt[0] == b'a') :
                        data = strpkt.split(":")
                        xyz = data[1].split(",")

                        if counter==0:
                            print "c:" + xyz[0] + " x:" + xyz[1] + " y:" + xyz[2] + "z:" + xyz[3]
                            with open(ACC_X_DATA_FILE, "a") as myfile:
                                myfile.write(xyz[1] + '\n')
                            with open(ACC_Y_DATA_FILE, "a") as myfile:
                                myfile.write(xyz[2] + '\n')
                            with open(ACC_Z_DATA_FILE, "a") as myfile:
                                myfile.write(xyz[3] + '\n')
                            with open(COMPASS_DATA_FILE, "a") as myfile:
                                myfile.write(xyz[0] + '\n')

                        else:
                            counter += 1
                            if counter == 10:
                                counter = 0

                        x = int(xyz[0])
                        y = int(xyz[1])
                        z = int(xyz[2])
                        qm.IMUData(xAxis=x, yAxis=y, zAxis=z)


                    elif (strpkt[0] == b'2') :
                        sonar2Data = convertPacketToSonarData(strpkt)
                    elif (strpkt[0] == b'3') :
                        sonar3Data = convertPacketToSonarData(strpkt)
                    elif (strpkt[0] == b'C') :
                        compassData = strpkt[2:5]

        except:
            sprotapi.SPROTClose()
            sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=SERIALMOD_BAUDRATE)

def remove_previous_data_files():
    os.remove(ACC_X_DATA_FILE)
    os.remove(ACC_Y_DATA_FILE)
    os.remove(ACC_Z_DATA_FILE)
    os.remove(COMPASS_DATA_FILE)

def begin_transmission():
    remove_previous_data_files()
    read_packet()

if __name__ == "__main__":
    begin_transmission()