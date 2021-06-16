import ctypes
from enum import Enum

DLE = 0x10
ETX = 0x03


class ReportPacketStructure(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("code", ctypes.c_uint8),
        ("timit", ctypes.c_uint16),
        ("timms", ctypes.c_uint32),
        ("freq", ctypes.c_float),
        ("ampl", ctypes.c_float),
    ]


class UARTPacket(ctypes.Union):
    _fields_ = [
        ("packet", ReportPacketStructure),
        ("buffer", ctypes.c_uint8*ctypes.sizeof(ReportPacketStructure))
    ]


class ParserStates(Enum):
    WAIT_DLE1 = 1
    WAIT_DATA = 2
    WAIT_DLE2 = 3


class UARTParserState():
    def __init__(self):
        self.state = ParserStates.WAIT_DLE1
        self.data_ready = False
        self.code = 0
        self.len = 0
        self.buffer = []
        self.packet = UARTPacket()

    def parse_byte(self, newbyte):
        self.data_ready = False
        if self.state == ParserStates.WAIT_DLE1:
            if newbyte == DLE:
                self.len = 0
                self.buffer = []
                self.state = ParserStates.WAIT_DATA
        elif self.state == ParserStates.WAIT_DATA:
            if newbyte == DLE:
                self.state = ParserStates.WAIT_DLE2
            else:
                self.buffer.append(newbyte)
                self.len += 1
        elif self.state == ParserStates.WAIT_DLE2:
            if newbyte == DLE:
                self.buffer.append(newbyte)
                self.len += 1
                self.state = ParserStates.WAIT_DATA
            elif newbyte == ETX:
                self.state = ParserStates.WAIT_DLE1
                self.data_ready = True
            else:
                self.len = 0
                self.state = ParserStates.WAIT_DLE1
                self.buffer = []
