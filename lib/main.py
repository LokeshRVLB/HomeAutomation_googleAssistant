from machine import Pin
from umqtt.simple import MQTTClient
from machine import I2C
import lcd16xn
import network
import time

def initiliseWifi():
    printLCD(("Connecting wifi"))
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    time.sleep(2)
    while not sta_if.isconnected():
    	sta_if.connect('new', 'RVLBlokesh')
    	time.sleep(2)
    	printLCD(("Connecting...."))
    printLCD(("Connected"))

def printLCD(msg):
    try:
        lcd.lcd_clear()
        i = 1
        for data in msg:
            lcd.lcd_display_string(data, i)
            i = i + 1;
    except Exception as e:
        print("no lcd found")

def defaultMsg():
    bulbStatus = "ON" if (bulb_pin.value() == 1) else "OFF"
    motorStatus = "ON" if (motor_pin.value() == 1) else "OFF"
    autoMode = "ON" if (automode == 1) else "OFF"
    printLCD(("Bulb : " + bulbStatus, "Motor:" + motorStatus + " AM: " + autoMode))

def motorControl(x):
    global automode
    if automode == 0:
        return
    if x.value() == 1:
        motar_pin.on()
    else:
        motar_pin.off()

def callBack(topic, msg):
    global automode
    print(str(msg))
    print(str(msg) == "b'off'")
    print(str(msg) == "b'on'")
    if str(msg) == "b'light off'":
        printLCD(("Swtching", "Lights off"))
        bulb_pin.off()
        time.sleep(2)
        defaultMsg()
    if str(msg) == "b'light on'":
        printLCD(("Swtching", "Lights on"))
        bulb_pin.on()
        time.sleep(2)
        defaultMsg()
    if str(msg) == "b'motor off'":
        if automode == 1:
            automode = 0
            moisture_sense.disable_irq()
        printLCD(("Swtching", "Motor off"))
        motor_pin.off()
        time.sleep(2)
        defaultMsg()
    if str(msg) == "b'motor on'":
        if automode == 1:
            automode = 0
        printLCD(("Swtching", "Motor on"))
        motor_pin.on()
        time.sleep(2)
        defaultMsg()
    if str(msg) == "b'automatic mode on'":
        printLCD(("automatic mode", "on"))
        automode = 1
        moisture_sense.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING , handler = motorControl)
        time.sleep(2)
        defaultMsg()
    if str(msg) == "b'automatic mode off'":
        printLCD(("automatic mode", "off"))
        automode = 0
        time.sleep(2)
        defaultMsg()

def main():
    print("initilising wifi")
    initiliseWifi()
    print("wifi initlised")
    time.sleep(2)
    defaultMsg()

    c = MQTTClient(server = "io.adafruit.com", client_id = "LokeshR", password = "b34331af72084d54aa122a028f0e5bb9")
    c.set_callback(callBack)
    c.connect()
    c.subscribe("LokeshR/feeds/switchcontrol")

    try:
        while True:
            c.wait_msg()
    finally:
            c.disconnect()

bulb_pin = Pin(2, Pin.OUT)
motor_pin = Pin(4, Pin.OUT)
automode = 0
moisture_sense = Pin(12, Pin.OUT)
i2c = I2C(scl = Pin(5), sda = Pin(4))
devices = i2c.scan()
if len(devices) == 0:
    print("no LCD display attached")
for data in devices:
    print("device address found: " + str(data))
time.sleep(1)
lcd = lcd16xn.lcd(i2c)
main()
