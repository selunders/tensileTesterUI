# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:39:08 2022

@author: Kevin Sikes

Manual Motor Control
Used to manually control the motor and clutches to roughly move the crosshead into place to prepare for a test. Can also be used to conduct a test without safety measures and with other vendor's software reading sensor data.

This was programmed in Spyder 5.0.5 with Python 3.8
The anaconda eviroment and packages used are included in the "Design Solutions/Code/Anaconda Enviroment"

To create a EXE: Auto py to exe works well in my experience
"""

import serial
import dearpygui.dearpygui as dpg
import logging
import time

#As a note: the reson for only having the serial ports open for the minimum amount of time is that if the program crashes while the port is open, it won't let go of the serial port without the usb being pulled out.

#%% For debugging
logging.basicConfig(level=logging.DEBUG)

#Virutal COM ports
GPIO_COM = "COM7"

#Is Motor Running
motorOn = False
#logging.debug("motorOn: "+str(motorOn))

#Sleep Times
sleepGPIO = 0.05 #Time for GPIO to process previous command
sleepRelayEng = .015 #Time for relays to engage
sleepRelayDiseng = .010 #Time for relays to disengage

#%%GUI
    
    
def toMoveMotor():
    logging.debug("toMoveMotor")
    global GPIO_COM
    global GPIO
    GPIO_COM = "COM"+str(dpg.get_value(GPIO_COM_GUI))
    logging.debug(GPIO_COM)
    GPIO = serial.Serial(GPIO_COM, 19200, timeout=1)
    GPIO.close()
    
    #Hide previous screen
    dpg.hide_item("txt_1")
    dpg.hide_item("txt_GPIO_COM")
    dpg.hide_item("int_GPIO_COM")
    dpg.hide_item("btn_toMoveMotor")
    #Show next screen
    dpg.show_item("txt_ManMtrCon")
    dpg.show_item("btn_MoveUp")
    dpg.show_item("btn_Stop")
    dpg.show_item("btn_MoveDown")

def runMotorUp():
    logging.debug("runMotorUp start")
    #Global variables
    #clutch that is activated. ONLY ONE OF THE CLUTCHES SHOULD BE ACTIVE AT A TIME (exception is clutch 3 for emergency break)
    #Check if motor is running to prevent multple clutches being activated at the same time
    global motorOn
    logging.debug("motorOn: "+str(motorOn))
    if(motorOn == True):
        logging.debug("Motor already running!")
        return

    #up clutch 1, pin 14 = E
    clutchPin=14
    logging.debug("Clutch 1")
    
    if (int(clutchPin) < 10):
        gpioClutchIndex = str(clutchPin)
    else:
        gpioClutchIndex = chr(55 + int(clutchPin))
    
    logging.debug("gpioClutchIndex: " + gpioClutchIndex)
    #open GPIO serial port
    GPIO.open()
    #engage clutch
    command = "gpio set "+ gpioClutchIndex + "\r"
    logging.debug(command)
    GPIO.write(command.encode())
    #wait for relay 10ms to engage, 5ms buffer
    logging.debug("sleep relay engage")
    time.sleep(sleepRelayEng)
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    #engage motor (pin 8)
    command = "gpio set "+ "8" + "\r"
    logging.debug(command)
    GPIO.write(command.encode())
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    motorOn = True
    logging.debug("motorOn: "+str(motorOn))
    #Close GPIO serial port
    GPIO.close()
    logging.debug("runMotorUp end")

def runMotorDown():
    logging.debug("runMotorDown start")
    #Global variables
    #clutch that is activated. ONLY ONE OF THE CLUTCHES SHOULD BE ACTIVE AT A TIME (exception is clutch 3 for emergency break)
    global gpioClutchIndex
    #Check if motor is running to prevent multple clutches being activated at the same time
    global motorOn
    logging.debug("motorOn: "+str(motorOn))
    if(motorOn == True):
        logging.debug("Motor already running!")
        return

    #down clutch 4, pin 11 = B
    clutchPin = 11
    logging.debug("Clutch 4")
    
    if (int(clutchPin) < 10):
        gpioClutchIndex = str(clutchPin)
    else:
        gpioClutchIndex = chr(55 + int(clutchPin))
    
    logging.debug("gpioClutchIndex: " + gpioClutchIndex)
    #open GPIO serial port
    GPIO.open()
    #engage clutch
    command = "gpio set "+ gpioClutchIndex + "\r"
    logging.debug(command)
    GPIO.write(command.encode())
    #wait for relay 10ms to engage, 5ms buffer
    logging.debug("sleep relay engage")
    time.sleep(sleepRelayEng)
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    #engage motor (pin 8)
    command = "gpio set "+ "8" + "\r"
    logging.debug(command)
    GPIO.write(command.encode())
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    motorOn = True
    logging.debug("motorOn: "+str(motorOn))
    #Close GPIO serial port
    GPIO.close()
    logging.debug("runMotorDown end")


def stopMotor():
    logging.debug("stopMotor start")
    #Global variables
    #if the motor hasn't been started, then it doesn't need to be stopped
    global motorOn
    logging.debug("motorOn: "+str(motorOn))

    #open GPIO serial port
    GPIO.open()
    #disengage motor (pin 8)
    command = "gpio clear "+ "8" + "\r"
    GPIO.write(command.encode())
    #wait for relay 5ms to disengag, 5ms buffer
    logging.debug("sleep relay disengage")
    time.sleep(sleepRelayDiseng)
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    #disengage clutches
    command = "gpio clear "+ chr(55 + int(14)) + "\r" #Clear pin 14 [Clutch 1]
    GPIO.write(command.encode())
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    command = "gpio clear "+ chr(55 + int(11)) + "\r" #Clear pin 11 [Clutch 4]
    GPIO.write(command.encode())
    
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    command = "gpio set "+ chr(55 + int(12)) + "\r" #Set pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    #give GPIO time to process previous command
    logging.debug("sleep for break + GPIO")
    time.sleep(1)
    command = "gpio clear "+ chr(55 + int(12)) + "\r" #Clear pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    #set the motor to off so it can be turned on later
    motorOn = False
    logging.debug("motorOn: "+str(motorOn))
    #Close GPIO serial port
    GPIO.close()
    logging.debug("stopMotor end")

    
#%%GUI

vp = dpg.create_viewport(title='Ice Breakers Move Motor', width=960, height=540)

with dpg.value_registry():
    GPIO_COM_GUI = dpg.add_int_value(default_value=7)

with dpg.window(id="win_Main", label="Ice Breakers", width=960, height=540, no_close=True, no_collapse=True):
    
    #Select Virtual COM ports for connected devices
    
    #VirCom
    
    dpg.add_text("If USB positions for devices are changed: \n1) Open Command Promt or PowerShell\n2) Type \'mode\' and hit enter\n3) Check that device Virtual COM ports match the below boxes",id="txt_1")
    
    dpg.add_text("GPIO (Usually COM port 7)",id="txt_GPIO_COM")
    
    dpg.add_input_int(id="int_GPIO_COM",label="GPIO",min_clamped=True,max_clamped=True,min_value=0, source = GPIO_COM_GUI)
    
    dpg.add_button(id="btn_toMoveMotor",label="Next Screen",callback=toMoveMotor)
    
    
    #MoveMotor
    
    dpg.add_text("Manual Motor Control: Click buttons one at a time\nTo switch directions, make sure that the \'Stop\' button is clicked before clicking on \'Up\' or \'Down\'\nTo exit: press the x in the top right corner",id="txt_ManMtrCon",show=False)
    
    dpg.add_button(id="btn_MoveUp",label="Up",callback=runMotorUp, show=False)
    dpg.add_button(id="btn_Stop",label="Stop",callback=stopMotor, show=False)
    dpg.add_button(id="btn_MoveDown",label="Down",callback=runMotorDown, show=False)
    
    
dpg.set_primary_window=("win_Main", True)
dpg.setup_dearpygui(viewport=vp)
dpg.show_viewport(vp)
dpg.start_dearpygui()