from machine import Pin
import machine
import time
import network
import socket
import time

from gpio_lcd import GpioLcd
import sdcard
import uos

from Si7021 import Si7021
from TSL2591 import TSL2591

class HomeController:
    def __init__(self):

        # Init Relais Pins
        self.relais = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

        # Init Status LED Pins
        self.statusLED ={"Green": Pin(28,Pin.OUT), "Yellow": Pin(27,Pin.OUT)}

        # Init Board Switch
        self.boardSwitch = Pin(3, Pin.IN)

        # Init LCD Display
        self.lcd = GpioLcd(rs_pin=Pin(15,Pin.OUT),
                          enable_pin=Pin(14,Pin.OUT),
                          d4_pin=Pin(20,Pin.OUT),
                          d5_pin=Pin(21,Pin.OUT),
                          d6_pin=Pin(22,Pin.OUT),
                          d7_pin=Pin(26,Pin.OUT),
                          num_lines=2, num_columns=16)
        self.lcd.clear()

        # Init SD Card
        cs = machine.Pin(17, machine.Pin.OUT)
        spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))
        
        self.sd = sdcard.SDCard(spi, cs)
        self.vfs = uos.VfsFat(self.sd)
        uos.mount(self.vfs, "/sd")

        # Init Si7021 Temperature and Humidity Sensor
        i2c = machine.I2C(id=1,scl=machine.Pin(7), sda=machine.Pin(6))
        self.si7021 = Si7021(i2c)

        # Init TSL2591 Light Sensor
        i2c = machine.I2C(id=0,scl=machine.Pin(5), sda=machine.Pin(4))
        self.tsl2591 = TSL2591(i2c)

        # Tun off all Outputs
        for relai in self.relais:
            relai.value(0)


        for led in self.statusLED:
            self.statusLED[led].value(0)    

        self.lcd.putstr("Startup Done.")

        # Init Wifi
        # ssid = 'YOUR NETWORK NAME'
        # password = 'YOUR NETWORK PASSWORD'

        # wlan = network.WLAN(network.STA_IF)
        # wlan.active(True)
        # wlan.connect(ssid, password)

    def set_relais(self, relai, value):
        if relai >= 0 and relai < 4 and value >= 0 and value <= 1:
            self.relais[relai].value(value)
            return True
        else:
            return False

    def set_status_led(self, led, value):
        if led in self.statusLED and value >= 0 and value <= 1:
            self.statusLED[led].value(value)
            return True
        else:
            return False
        
    def get_board_switch(self):
        return self.boardSwitch.value()
    
    def write_lcd(self, text):
        self.lcd.clear()
        self.lcd.putstr(text)

    def clear_lcd(self):
        self.lcd.clear()


    def get_temperature(self):
        return self.si7021.read_temperature()

    
    def get_humidity(self):
        return self.si7021.read_humidity()
    
    def get_light(self):
        return self.tsl2591.read_lux()


