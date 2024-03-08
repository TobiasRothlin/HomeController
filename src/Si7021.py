import time

class Si7021:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x40

    def read_temperature(self):
        self.i2c.writeto(self.addr, b'\xF3')
        time.sleep(0.015)
        rawResponse = self.i2c.readfrom(self.addr, 2)
        temp = (rawResponse[0] << 8) | rawResponse[1]
        temp = (175.72 * temp / 65536) - 46.85
        return temp

    def read_humidity(self):
        self.i2c.writeto(self.addr, b'\xF5')
        time.sleep(0.030)
        rawResponse = self.i2c.readfrom(self.addr, 2)
        humidity = (rawResponse[0] << 8) | rawResponse[1]
        humidity = (125 * humidity / 65536) - 6
        return humidity