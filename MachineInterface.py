# We need the following commands here or in other modules:
    # Motor
        # Move Motor Up
        # Move Motor Down
        # Stop Motor
    # Read Sensors
        # readDSCUSB
        # readLoadCell
    # Run Tests
        # runTest
        # endTest
    # IO
        # writeFile

import serial
import dearpygui.dearpygui as dpg
import time


GPIO_COM = None
GPIO = None 
GPIO_IS_INIT = False

#Sleep Times
sleepGPIO = 0.05 #Time for GPIO to process previous command
sleepRelayEng = .015 #Time for relays to engage
sleepRelayDiseng = .010 #Time for relays to disengage

# motor_is_running = false

def get_gpio_info():
    global GPIO_IS_INIT
    global GPIO
    global GPIO_COM

    GPIO_COM = "COM"+str(dpg.get_value("GPIO_COM_GUI"))
    GPIO = serial.Serial(GPIO_COM, 19200, timeout=1)
    GPIO.close()
    GPIO_IS_INIT = True
    print(f'GPIO_COM is {GPIO_COM}, GPIO is {GPIO}')

def motor_down():
    global GPIO_IS_INIT
    global GPIO

    if not GPIO_IS_INIT:
        print("GPIO not initialized")
        return
    clutchPin = 11
    GPIO.open()

    command = "gpio set " + chr(55 + int(clutchPin)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayEng)
    time.sleep(sleepGPIO)

    command = "gpio set " + "8" +"\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    
    GPIO.close()

def motor_up():
    global GPIO_IS_INIT
    global GPIO

    if not GPIO_IS_INIT:
        print("GPIO not initialized")
        return
    clutchPin = 14
    GPIO.open()

    command = "gpio set " + chr(55 + int(clutchPin)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayEng)
    time.sleep(sleepGPIO)

    command = "gpio set " + "8" +"\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    
    GPIO.close()


def motor_stop():
    global GPIO_IS_INIT
    global GPIO

    if not GPIO_IS_INIT:
        print("GPIO not initialized")
        return
    GPIO.open()

    command = "gpio clear 8\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayDiseng)
    time.sleep(sleepGPIO)

    command = "gpio clear " + chr(55+int(11)) + "\r"
    GPIO.write(command.encode())

    command = "gpio clear " + chr(55+int(14)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    command = "gpio set " + chr(55 + int(12)) + "\r" #Set pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    time.sleep(1) #longer sleep time for break
    
    command = "gpio clear " + chr(55 + int(12)) + "\r" #Clear pin 12 [Clutch 3] = break
    
    GPIO.write(command.encode())
    GPIO.close()

    # Direction
    # Pausing
    # Fix axis labels, check
    # Report some data from the test?
    # Force cutoff/displacement
    # Initializing machine