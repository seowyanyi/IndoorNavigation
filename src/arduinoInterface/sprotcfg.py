###### Protocol constants #######

SPROT_PROTOCOL_MARKER =	             0xAA			  # Protocol marker
PACKET_SIZE =                        32                           # N-bytes fixed packet size
HEADER_LENGTH =                      2                            # Header size in bytes
FIELD_DLEN_LENGTH =                  1                            # DATA_LENGTH field size in bytes
FIELD_CHECKSUM_LENGTH =              1                            # CHECKSUM field size in bytes

# The length of the DATA field in bytes
FIELD_DATA_LENGTH =                 (PACKET_SIZE - HEADER_LENGTH - FIELD_CHECKSUM_LENGTH)

FIELD_PM_OFFSET =                    0                            # Protocol marker offset in bytes
FIELD_DLEN_OFFSET =                  1                            # DATA_LENGTH field offset in bytes
FIELD_CHECKSUM_OFFSET =              PACKET_SIZE - 1              # CHECKSUM field offset in bytes
FIELD_DATA_OFFSET =                  HEADER_LENGTH                # DATA field offset in bytes

# Timeout Parameters in secs
SPROT_SEND_TIMEOUT =                 5                            # Default send timeout in ms
SPROT_RECV_TIMEOUT =                 600                          # Default receive timeout ms

# Generic error constant
SPROT_ERROR =                        -1

#Default baudrate to be used
DEFAULT_BAUDRATE =                   9600

