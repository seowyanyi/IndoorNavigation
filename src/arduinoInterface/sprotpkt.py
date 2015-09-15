# SPROTPacket class represents a Serial Protocol Packet

# Constructor :
# SPROTPacket(rawPacket=none)
#    rawPacket - A bytearray or bytes that contains the raw packet data

import sprotcfg as sprotcfg


class SPROTPacket:
    def __init__(self, rawPacket=None):
        if(rawPacket == None):
			self.protocolMarker = sprotcfg.SPROT_PROTOCOL_MARKER
			self.dataLength = 0;
			self.data = None
			self.checksum = 0
			self.raw = None
        else :
			# Construct packet from given array of bytes
			self.protocolMarker = [sprotcfg.FIELD_PM_OFFSET]
			self.dataLength = rawPacket[sprotcfg.FIELD_DLEN_OFFSET]
			self.data = bytearray(rawPacket[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET + self.dataLength])
			self.checksum = rawPacket[sprotcfg.FIELD_CHECKSUM_OFFSET]
			self.raw = rawPacket
     
    def toByteArray(self):
        self.raw = bytearray(sprotcfg.PACKET_SIZE)
        self.raw[sprotcfg.FIELD_PM_OFFSET] = sprotcfg.SPROT_PROTOCOL_MARKER
        self.raw[sprotcfg.FIELD_DLEN_OFFSET] = len(self.data);
        self.raw[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET+len(self.data)] = self.data
        self.raw[sprotcfg.FIELD_CHECKSUM_OFFSET] = self.checksum
        return self.raw

    def printPacket(self):
##        print "pktinfo : DLEN=", self.dataLength, "  DATA=", self.data, "  CKS=", format(self.checksum, "02x")
        print "DATA=", self.data


