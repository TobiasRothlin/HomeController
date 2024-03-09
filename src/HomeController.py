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
        self.log_idx = 0

        # Init Relais Pins
        self.relais = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

        # Init Status LED Pins
        self.statusLED ={"Green": Pin(28,Pin.OUT), "Yellow": Pin(27,Pin.OUT)}

        # Init Board Switch
        self.boardSwitch = Pin(3, Pin.IN)

        self.boardSwitch.irq(trigger=Pin.IRQ_FALLING, handler=self.board_switch_handler)

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
        self.sd_connected = False
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
        
        try:
            self.sd = sdcard.SDCard(spi, cs)
            self.vfs = uos.VfsFat(self.sd)
            uos.mount(self.vfs, "/sd")
            self.sd_connected = True

        except Exception as e:
            print("Error: ", e)
            print("SD Card not found")


        # Create New Log File unique file
        if self.sd_connected:
            self.file_name = "log.csv"
            index = 0
            while self.file_name in uos.listdir("/sd"):
                self.file_name = self.file_name.split(".")[0].split("_")[0] + f"_{index}.csv"
                index += 1

            self.file_name = "/sd/" + self.file_name
            print("Creating new Log File: ", self.file_name)
            with open(self.file_name, "w") as f:
                f.write("Temperature,Humidity,Light\n")

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

        # Init Wifi10
        ssid = 'WalterRothlin_2'
        password = 'waltiClaudia007'

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        # Set static IP
        ip = '192.168.1.21'  # The desired static IP
        subnet_mask = '255.255.255.0'  # The subnet mask for your network
        gateway = '192.168.1.1'  # The gateway IP for your network
        dns_server = '8.8.8.8'  # The DNS server IP, here Google's DNS is used

        #self.wlan.ifconfig((ip, subnet_mask, gateway, dns_server))

        

        self.write_lcd(f"Connecting to {ssid}") 
        time.sleep(1)
        self.clear_lcd()
        itter = 1
        while not self.wlan.isconnected():
            time.sleep(1)
            self.write_lcd(itter*".")
            itter += 1
            if itter > 15:
                itter = 1   

        self.clear_lcd()
        network_info = self.wlan.ifconfig()
        self.write_lcd(f"IP:{network_info[0]}")


    def set_relais(self, relai, value):
        if relai >= 0 and relai < 4 and value >= 0 and value <= 1:
            self.relais[relai].value(value)
            return True
        else:
            return False

    def get_relais(self, relai):
        if relai >= 0 and relai < 4:
            return self.relais[relai].value()
        else:
            return None

    def set_status_led(self, led, value):
        if led in self.statusLED and value >= 0 and value <= 1:
            self.statusLED[led].value(value)
            return True
        else:
            return False

    def get_status_led(self, led):
        if led in self.statusLED:
            return self.statusLED[led].value()
        else:
            return None
        
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


    def board_switch_handler(self, pin):
        print("Board Switch Pressed")
        self.lcd.clear()


    def log_data(self):
        if self.sd_connected:
            self.set_status_led("Green", 1)
            self.log_idx += 1
            temp = self.get_temperature()
            hum = self.get_humidity()
            light = self.get_light()
            print(f"Idx: {self.log_idx} ,Temp: {temp}, Hum: {hum}, Light: {light}")
            self.write_lcd(f"Logging Data: {self.log_idx}")
            with open(self.file_name, "a") as f:
                f.write(f"{temp},{hum},{light}\n")

            self.set_status_led("Green", 0)
            self.set_status_led("Yellow", 0)
        else:
            print("SD Card not connected")
            self.set_status_led("Yellow", 1)