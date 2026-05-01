import time

class BH1750():
    def __init__(self, i2c, address=0x23):
        self.i2c = i2c
        self.address = address
        self.setup()

    def setup(self):
        self.i2c.writeto(self.address, b'\x01') # Power on
        self.i2c.writeto(self.address, b'\x10') # High Res Mode

    def read(self):
        data = self.i2c.readfrom(self.address, 2)
        # Converte os 2 bytes recebidos em Lux
        lux = ((data[0] << 8) | data[1]) / 1.2
        return lux