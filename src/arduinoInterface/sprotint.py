# Serial Protocol internal function definitions

import sprotcfg as sprotcfg
import sprotapi as sprotapi
import sprotpkt as sprotpkt


def createPacket(data):
    
    rawPacket = bytearray(sprotcfg.PACKET_SIZE)
    rawPacket[sprotcfg.FIELD_PM_OFFSET] = sprotcfg.SPROT_PROTOCOL_MARKER
    rawPacket[sprotcfg.FIELD_DLEN_OFFSET] = len(data);
    rawPacket[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET+len(data)] = data
    rawPacket[sprotcfg.FIELD_CHECKSUM_OFFSET] = generateChecksum(packet)
    packet = sprotpkt.SPROTPacket(rawPacket)

    return packet


def generateChecksum(packet):
    
    checksum = 0
    
    for i in range(sprotcfg.PACKET_SIZE-1) :
        checksum = checksum ^ packet.raw[i]
    
    return checksum


def receivePacket(timeout=sprotcfg.SPROT_RECV_TIMEOUT):
        
    sprotapi.serialPort.timeout = timeout
    readResult = sprotapi.serialPort.read(sprotcfg.PACKET_SIZE)
    recvBytes = bytearray(readResult)
    if (len(recvBytes) < sprotcfg.PACKET_SIZE):
        print "errorhere"
        return sprotcfg.SPROT_ERROR
    
    packet = sprotpkt.SPROTPacket(recvBytes)
            
    # Check for errors
    checksum = generateChecksum(packet)

    if (checksum != packet.checksum) :    
        return sprotcfg.SPROT_ERROR
    else :
        return packet
    

def sendPacket(packet):
    sprotapi.serialPort.write(packet.toByteArray())
