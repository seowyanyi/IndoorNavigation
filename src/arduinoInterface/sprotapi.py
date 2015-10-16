# python module containing serial port functions utilizing Serial Protocol (sprot)

import serial as serial
import sprotcfg as sprotcfg
import sprotint as sprotint
import sprotapi as sprotapi
import sprotpkt as sprotpkt

serialPort = None
sprotapi.initialized = False

def SPROTInit(portName, baudrate=115200):
	if sprotapi.initialized :
		return
	else :
		sprotapi.serialPort = serial.Serial(portName, baudrate=baudrate, timeout=sprotcfg.SPROT_RECV_TIMEOUT)
		serialPort.flushInput()
		serialPort.flushOutput()
		sprotapi.initialized = True

		
def SPROTClose():
	serialPort.flushInput()
	#serialPort.flushOutput()
	serialPort.close()
	sprotapi.initialized = False
	
	
def SPROTReceive(timeout=sprotcfg.SPROT_RECV_TIMEOUT):
	
	if not sprotapi.initialized :
		return sprotcfg.SPROT_ERROR
        else :
		return sprotint.receivePacket(timeout)
		
	
def SPROTSend(data, timeout=sprotcfg.SPROT_SEND_TIMEOUT):

	if (not sprotapi.sessionStarted and (sprotint.startSession(timeout) == -1)) :
		return sprotcfg.SPROT_ERROR
	
	packet = sprotint.createPacket(data)
	sprotint.sendPacket(packet)

def SPROTFlush():
    serialPort.flush()	
