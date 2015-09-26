import sprotapi as sprotapi
import sprotpkt as sprotpkt
import serialmod as serialmod
import queueManager as qm
DATA_SIZE = 16
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004
SERIALMOD_BAUDRATE = 115200


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
counter = 0       

# Strips trailing zeroes if required
def removeNullChars(str):
    maxIndex = 7
    for i in range(maxIndex):
        if(str[i].isdigit() or str[i] == '.'):
            maxIndex = i

    return str[0:maxIndex+1]
    
        
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

                    if(counter==0):
                        print "c:" + xyz[0] + " x:" + xyz[1] + " y:" + xyz[2] + "z:" + xyz[3]
                    else:
                        counter = counter + 1
                        if(counter == 15):
                            counter = 0;

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


# End of serialmod
