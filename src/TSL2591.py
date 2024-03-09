import machine
import time
from builtins import hex

TSL2591_REGISTER_ENABLE = 0x00     
TSL2591_REGISTER_CONTROL = 0x01     
TSL2591_REGISTER_THRESHOLD_AILTL = 0x04
TSL2591_REGISTER_THRESHOLD_AILTH = 0x05
TSL2591_REGISTER_THRESHOLD_AIHTL = 0x06
TSL2591_REGISTER_THRESHOLD_AIHTH = 0x07
TSL2591_REGISTER_THRESHOLD_NPAILTL =0x08 
TSL2591_REGISTER_THRESHOLD_NPAILTH =0x09
TSL2591_REGISTER_THRESHOLD_NPAIHTL =0x0A
TSL2591_REGISTER_THRESHOLD_NPAIHTH =0x0B
TSL2591_REGISTER_PERSIST_FILTER = 0x0C 
TSL2591_REGISTER_PACKAGE_PID = 0x11    
TSL2591_REGISTER_DEVICE_ID = 0x12      
TSL2591_REGISTER_DEVICE_STATUS = 0x13 
TSL2591_REGISTER_CHAN0_LOW = 0x14     
TSL2591_REGISTER_CHAN0_HIGH = 0x15    
TSL2591_REGISTER_CHAN1_LOW = 0x16  
TSL2591_REGISTER_CHAN1_HIGH = 0x17  

TSL2591_COMMAND_BIT = 0xA0
TSL2591_CLEAR_INT = 0xE4
TSL2591_WORD_BIT = 0x20
TSL2591_BLOCK_BIT = 0x10
TSL2591_ENABLE_POWEROFF = 0x00
TSL2591_ENABLE_POWERON = 0x01
TSL2591_ENABLE_AEN = 0x02
TSL2591_ENABLE_AIEN = 0x10
TSL2591_ENABLE_NPIEN = 0x80
TSL2591_LUX_DF = 408.0
TSL2591_LUX_COEFB = 1.64
TSL2591_LUX_COEFC = 0.59
TSL2591_LUX_COEFD = 0.86

TSL2591_PERSIST_EVERY = 0x00
TSL2591_PERSIST_ANY = 0x01 
TSL2591_PERSIST_2 = 0x02 
TSL2591_PERSIST_3 = 0x03  
TSL2591_PERSIST_5 = 0x04  
TSL2591_PERSIST_10 = 0x05  
TSL2591_PERSIST_15 = 0x06  
TSL2591_PERSIST_20 = 0x07  
TSL2591_PERSIST_25 = 0x08  
TSL2591_PERSIST_30 = 0x09  
TSL2591_PERSIST_35 = 0x0A  
TSL2591_PERSIST_40 = 0x0B  
TSL2591_PERSIST_45 = 0x0C  
TSL2591_PERSIST_50 = 0x0D  
TSL2591_PERSIST_55 = 0x0E  
TSL2591_PERSIST_60 = 0x0F  

TSL2591_GAIN_LOW = 0x00
TSL2591_GAIN_MED = 0x10
TSL2591_GAIN_HIGH = 0x20
TSL2591_GAIN_MAX = 0x30

class TSL2591:
    """
    A class representing the TSL2591 light sensor.

    Args:
        i2c: The I2C bus object.
        address (int): The I2C address of the sensor (default: 0x29).

    Attributes:
        i2c: The I2C bus object.
        address (int): The I2C address of the sensor.

    """

    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self.scan()
        self.get_id()

    def scan(self):
        """
        Scans for I2C devices and prints their addresses in hexadecimal format.
        """
        devices = self.i2c.scan()
        print(f"Devices: {','.join([hex(device) for device in devices])}")

    def get_id(self):
        """
        Reads the ID of the sensor and prints it in hexadecimal format.
        """
        # Read ID from Register 0x12
        self.i2c.writeto(self.address, bytearray([TSL2591_COMMAND_BIT | TSL2591_REGISTER_DEVICE_ID]))
        rawResponse = self.i2c.readfrom(self.address, 1)
        print(f"ID: {hex(rawResponse[0])}")

    def enable(self):
        """
        Enables the sensor by writing the appropriate values to the enable register.
        """
        self.i2c.writeto_mem(self.address, TSL2591_COMMAND_BIT | TSL2591_REGISTER_ENABLE, bytearray([TSL2591_ENABLE_POWERON | TSL2591_ENABLE_AEN | TSL2591_ENABLE_AIEN |
             TSL2591_ENABLE_NPIEN]))

    def disable(self):
        """
        Disables the sensor by writing the appropriate values to the enable register.
        """
        self.i2c.writeto_mem(self.address, TSL2591_COMMAND_BIT | TSL2591_REGISTER_ENABLE,bytearray([TSL2591_ENABLE_POWEROFF]))

    def read_raw(self):
        """
        Reads the raw values from the sensor and returns them as a tuple (ch0, ch1).

        Returns:
            tuple: A tuple containing the raw values of channel 0 (ch0) and channel 1 (ch1).
        """
        self.enable()
        time.sleep(0.5)
        self.i2c.writeto(self.address, bytearray([TSL2591_COMMAND_BIT | TSL2591_REGISTER_CHAN0_LOW]))
        rawResponse = self.i2c.readfrom(self.address, 4)
        ch0 = rawResponse[1] << 8 | rawResponse[0]
        ch1 = rawResponse[3] << 8 | rawResponse[2]

        self.disable()
        return ch0, ch1

    def read_lux(self):
        """
        Reads the lux value from the sensor.

        Returns:
            float: The lux value.
        """
        ch0, ch1 = self.read_raw()
        return self.calculate_lux(ch0, ch1)

    def calculate_lux(self, ch0, ch1):
        """
        Calculates the lux value based on the raw channel values.

        Args:
            ch0 (int): The raw value of channel 0.
            ch1 (int): The raw value of channel 1.

        Returns:
            float: The lux value.
        """
        if ch0 == 0:
            return 0
        d0 = ch0 * (402.0 / 65535.0)
        d1 = ch1 * (402.0 / 65535.0)
        ratio = d1 / d0

        if ratio < 0.5:
            return (0.0304 * d0) - (0.062 * d0 * (pow(d1 / d0, 1.4)))
        elif ratio < 0.61:
            return (0.0224 * d0) - (0.031 * d1)
        elif ratio < 0.80:
            return (0.0128 * d0) - (0.0153 * d1)
        elif ratio < 1.30:
            return (0.00146 * d0) - (0.00112 * d1)
        else:
            return 0
