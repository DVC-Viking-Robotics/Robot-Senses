import board
from busio import I2C, SPI

I2C_BUS = I2C(board.SDA, board.SCL)
SPI_BUS = SPI(board.MISO, board.MOSI, board.SCK)

class Serial_Manager:
    def __init__(self, ser_objects=None):
        self._mgr = []
        if ser_objects is not None:
            for ser in ser_objects:
                self.insert(ser)

    @property
    def get_ports(self):
        result = []
        for obj in self._mgr:
            result.insert(obj.port)
        return result
    
    def insert(self, obj, index=None):
        self._mgr.insert(len(self._mgr) - 1 if index is None else index, obj)

    def remove(self, port):
        for i, obj in enumerate(self._mgr):
            if obj.port == port:
                self._mgr.remove(i)

    def get_obj(self, port):
        for obj in self._mgr:
            if obj.port == port:
                return obj
        return None

SER_MGR = Serial_Manager()