# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 15:31:54 2022

@author: Kevin Sikes

Code used to run a tensile test and read all of the sensor data. Has safety measures to stop the test if the extensometer elongation or load cell force gets too high. All vir COM port sensors need to be connected for this program to work.

This was programmed in Spyder 5.0.5 with Python 3.8
The anaconda eviroment and packages used are included in the "Design Solutions/Code/Anaconda Enviroment"

To create a EXE: Auto py to exe works well in my experience
"""

#%%Notes
#The reson for only having the serial ports open for the minimum amount of time is that if the program crashes while the port is open, it won't let go of the serial port without the usb being pulled out.

#%%Imports
import serial
import dearpygui.dearpygui as dpg
import logging
import time
import datetime

#%% For debugging
logging.basicConfig(level=logging.DEBUG)

#%% Declare Global and Constant variables
StopTest = False
ExtensometerRemoved = False
timeStartTest = 0

#data arrays
DSCUSB_data = []
LoadCell_data = []
#RotaryEncoder_Data = []
time_data = []

#Virutal COM ports
DSCUSB_COM = "COM5"
LoadCell_COM = "COM3"
GPIO_COM = "COM7"

#Sleep Times
sleepGPIO = 0.05 #Time for GPIO to process previous command
sleepRelayEng = .015 #Time for relays to engage
sleepRelayDiseng = .010 #Time for relays to disengage

#load cell force max and extensometer elongation max
#FOR NOW THESE ARE HARD CODED. NEEDS TO BE ADDED TO GUI
FORCE_MAX = 3000
ELONG_MAX = 3

#Test
timeStartTest = -1

#%% GUI functions

def updateGraph():
    logging.debug("UpdateGraph")
    #extensometer graph
    if(dpg.get_value(removeExtensometer_GUI) == 0):#0 means extensometer connected, otherwise it is disconnected
        dpg.set_value("series_Elong", [time_data, DSCUSB_data])
        dpg.set_axis_limits("ETimeAxis", 0, max(time_data)+1)
        dpg.set_axis_limits("ElongationAxis", min(DSCUSB_data)-.2, max(DSCUSB_data)+.2)
    #Load cell graph
    dpg.set_value("series_Force", [time_data, LoadCell_data])
    dpg.set_axis_limits("FTimeAxis", 0, max(time_data)+1)
    dpg.set_axis_limits("ForceAxis", min(LoadCell_data)-.5, max(LoadCell_data)+.5)
    
def toVirCOM():
    logging.debug("toVirCOM")
    
    #Hide elements from previous screen
    dpg.hide_item("btn_runTest")
    dpg.hide_item("int_removeExtensometer")
    dpg.hide_item("btn_toVirCOM")
    
    #Show items for next screen
    dpg.show_item("txt_1")
    dpg.show_item("txt_DSCUSB_COM")
    dpg.show_item("int_DSCUSB_COM")
    dpg.show_item("txt_LoadCell_COM")
    dpg.show_item("int_LoadCell_COM")
    dpg.show_item("txt_GPIO_COM")
    dpg.show_item("int_GPIO_COM")
    dpg.show_item("btn_toRunTest")
    
    
def toRunTest():
    logging.debug("toRunTest")
    
    #declare virual com ports as gloabl so they can be used in other methods
    #DSCUSB extensometer signal conditioner
    global DSCUSB
    global DSCUSB_COM
    #get COM port from GUI variable
    DSCUSB_COM = "COM"+str(dpg.get_value(DSCUSB_COM_GUI))
    logging.debug("DSCUSB_COM: " + DSCUSB_COM)
    #declare and open serial port
    DSCUSB = serial.Serial(port=DSCUSB_COM, baudrate=115200, bytesize=8, stopbits=serial.STOPBITS_ONE)
    #close serial port
    DSCUSB.close()
    
    #Load Cell signal conditioner
    global LoadCell
    global LoadCell_COM
    #get COM port from GUI variable
    LoadCell_COM = "COM"+str(dpg.get_value(LoadCell_COM_GUI))
    logging.debug("LoadCell_COM: " + LoadCell_COM)
    #declare and open serial port
    LoadCell = serial.Serial(port=LoadCell_COM, baudrate=115200, bytesize=8, stopbits=serial.STOPBITS_ONE)
    #close serial port
    LoadCell.close()
    
    #Numato 16 ChannelUSB GPIO
    global GPIO
    global GPIO_COM
    #get COM port from GUI variable
    GPIO_COM = "COM"+str(dpg.get_value(GPIO_COM_GUI))
    logging.debug("GPIO_COM: " + GPIO_COM)
    #declare and open serial port
    GPIO = serial.Serial(GPIO_COM, 19200, timeout=1)
    #close serial port
    GPIO.close()
    
    #Hide elements from previous screen
    dpg.hide_item("txt_1")
    dpg.hide_item("txt_DSCUSB_COM")
    dpg.hide_item("int_DSCUSB_COM")
    dpg.hide_item("txt_LoadCell_COM")
    dpg.hide_item("int_LoadCell_COM")
    dpg.hide_item("txt_GPIO_COM")
    dpg.hide_item("int_GPIO_COM")
    dpg.hide_item("btn_toRunTest")
    
    #Show elements for next screen
    dpg.show_item("btn_runTest")
    dpg.show_item("int_removeExtensometer")
    dpg.show_item("btn_toVirCOM")

#%%Read Sensor Functions

def readDSCUSB():
    logging.debug("Begin readDSCUSB")
    #Open serial port
    DSCUSB.open()
    #Command that reads data from DSCUSB
    command = '!001:SYS?\r'
    #Debugging
    logging.debug(command)
    #string to hold data sent from DSCUSB
    data = ""
    #Send command to DSCUSB
    DSCUSB.write(command.encode())
    #initalize data string with first read value
    data = DSCUSB.read()
    #While the last character of the data string is NOT a return character, keep reading data.
    while (data.decode("Ascii")[-1] != "\r"):
        data += DSCUSB.read()
    #Acknowlege DSCUSB with read data
    DSCUSB.write((data.decode("Ascii") + "\r").encode())
    #Close Serial port while not in use
    DSCUSB.close()
    #Used for debugging
    logging.debug(data)
    #get all of the float data and remove the return charater at the end
    floatData = float(data.decode("Ascii")[0:-1])
    
    logging.debug("End readDSCUSB")
    return floatData

def readLoadCell():
    logging.debug("readLoadCell start")
    #Open serial port
    LoadCell.open()
    #Command that reads data from Load Cell
    command = 'P\r'
    #Debugging
    logging.debug(command)
    #string to hold data sent from Load Cell
    data = ""
    #Send command to Load Cell
    LoadCell.write(command.encode())
    #initalize data string with first read value (MAY NEED TO READ 2 OR 3 TIMES TO GET PAST \r\n)
    data = LoadCell.read()
    #While the last character of the data string is NOT a return character, keep reading data.
    while (data.decode("Ascii")[-1] != "\r"):
        data += LoadCell.read()
    #Close Serial port while not in use
    LoadCell.close()
    #Used for debugging
    logging.debug("data:" + data.decode("Ascii"))
    
    #get loaction of " " to parse data (data format is "xxx.xxx LB")
    i = 0
    while(True):
        if(data.decode("Ascii")[i:i+1] == " "):
            break
        i +=1
    floatData = float(data.decode("Ascii")[0:i])
    #get the float from the string
    
    logging.debug("readLoadCell end")
    return floatData



#%%Motor Functions

def runMotorDown():
    logging.debug("runMotorDown start")
    #down clutch 4, pin 11 = B
    clutchPin = 11
    logging.debug("Clutch 4")
    
    #logging.debug("gpioClutchIndex: " + gpioClutchIndex)
    logging.debug("gpioClutchIndex: " + chr(55 + int(clutchPin)))
    
    #open GPIO serial port
    GPIO.open()
    
    #engage clutch
    command = "gpio set "+ chr(55 + int(clutchPin)) + "\r"
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
    #Close GPIO serial port
    GPIO.close()
    logging.debug("runMotorDown end")

def stopMotor():
    logging.debug("stopMotor start")
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
    command = "gpio clear "+ chr(55 + int(11)) + "\r" #Clear pin 11 [Clutch 4]
    GPIO.write(command.encode())
    
    #give GPIO time to process previous command
    logging.debug("sleep for GPIO")
    time.sleep(sleepGPIO)
    command = "gpio set "+ chr(55 + int(12)) + "\r" #Set pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    #give GPIO time to process previous command
    logging.debug("sleep for break + GPIO")
    time.sleep(1) #longer sleep time for break
    command = "gpio clear "+ chr(55 + int(12)) + "\r" #Clear pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    #Close GPIO serial port
    GPIO.close()
    logging.debug("stopMotor end")

#%%Main testing functions

def runTest():
    logging.debug("runTest start")
    
    global stopTest
    global timeStartTest
    #Hide GUI items that are not needed durning test
    dpg.hide_item("btn_runTest")
    dpg.hide_item("int_removeExtensometer")
    dpg.hide_item("btn_toVirCOM")
    dpg.hide_item("btn_toEndTest")
    
    dpg.show_item("int_stopTest")
    
    #activate the motor
    runMotorDown()
    #if the time that the test starts has not been recorded, then set it (this also prevents it from being overwritten if the test is stopped and re-started)
    if(timeStartTest == -1):
        timeStartTest = time.time()
    #Read sensor loop
    while(True):
        #record time
        time_data.append(time.time()-timeStartTest)
        #read extensometer if it is still connected
        if(dpg.get_value(removeExtensometer_GUI) == 0):#0 means extensometer connected, otherwise it is disconnected
            DSCUSB_data.append(readDSCUSB())
        #read load cell
        LoadCell_data.append(readLoadCell())
        updateGraph()
        #if stopTest_GUI is not default value, the extensometer reading is too large and still connected, or load cell exceeds safety value then stop the test
        if(dpg.get_value(stopTest_GUI) == 1 or ((abs(DSCUSB_data[-1]) > ELONG_MAX) and (dpg.get_value(removeExtensometer_GUI) != 0)) or abs(LoadCell_data[-1]) > FORCE_MAX):
            stopMotor()
            dpg.set_value(stopTest_GUI, 0)
            dpg.show_item("btn_runTest")
            dpg.show_item("int_removeExtensometer")
            dpg.show_item("btn_toVirCOM")
            dpg.show_item("btn_toEndTest")
            dpg.hide_item("int_stopTest")
            break
        #time.sleep(.1)

def toEndTest():
    #hide GUI elements so test can't be started again and this method can't be called more than once (which would cause duplicate data)
    dpg.hide_item("btn_runTest")
    dpg.hide_item("int_removeExtensometer")
    dpg.hide_item("btn_toVirCOM")
    dpg.hide_item("btn_toEndTest")
    
    #Write all sensor and time data to file
    writeFile()
    
    #Tell user to kill program after file is done writing
    dpg.show_item("txt_endTest")

def writeFile():
    #creats a timestamped file name with Year-Month-Day_Hour_minute_Second.csv so each file name should be unique
    fileName = "Tensile_Test_"+ str(datetime.datetime.now().strftime("%Y-%m-%d-%I_%M_%S_%p")) + ".csv"
    #create/open file and append append an ywritten data
    file = open(fileName,"a")
    #write time data
    file.write("Time,")
    for dataT in time_data:
        file.write(str(dataT))
        file.write(",")
    file.write("\n")
    #write extensometer data
    file.write("Elongation,")
    for dataE in DSCUSB_data:
        file.write(str(dataE))
        file.write(",")
    file.write("\n")
    #write load cell data
    file.write("Force,")
    for dataF in LoadCell_data:
        file.write(str(dataF))
        file.write(",")
    file.write("\n")
    #close file
    file.close()

#%%GUI

vp = dpg.create_viewport(title='Ice Breakers Tensile Test', width=1920, height=1080)

#This is used to hold all values in the GUI that need to be read and used elsewhere in the program
with dpg.value_registry():
    #bool_value = dpg.add_bool_value(default_value=True)
    DSCUSB_COM_GUI = dpg.add_int_value(default_value=6)
    LoadCell_COM_GUI = dpg.add_int_value(default_value=8)
    GPIO_COM_GUI = dpg.add_int_value(default_value=7)
    removeExtensometer_GUI = dpg.add_int_value(default_value=0)
    stopTest_GUI = dpg.add_int_value(default_value=0)

#Main testing window
with dpg.window(id="win_Main", label="Ice Breakers", width=960, height=1080, no_close=True, no_collapse=True):

    #VirCom - Select Virtual COM ports for connected devices
    
    dpg.add_text("If USB positions for devices are changed: \n1) Open Command Prompt or PowerShell\n2) Remove ALL USB devices\n3) Plug in one USB at a time and type \'mode\' and hit enter in command prompt\n4) Check if that device's Virtual COM port matches the boxes below",id="txt_1")
    
    dpg.add_text("DSCUSB (Usually COM port 6)",id="txt_DSCUSB_COM")
    
    dpg.add_input_int(id="int_DSCUSB_COM",label="DSCUSB",min_clamped=True,max_clamped=True,min_value=0, source = DSCUSB_COM_GUI)
    
    dpg.add_text("Load Cell (Usually COM port X)",id="txt_LoadCell_COM")
    
    dpg.add_input_int(id="int_LoadCell_COM",label="Load Cell",min_clamped=True,max_clamped=True,min_value=0, source = LoadCell_COM_GUI)
    
    dpg.add_text("GPIO (Usually COM port 7)",id="txt_GPIO_COM")
    
    dpg.add_input_int(id="int_GPIO_COM",label="GPIO",min_clamped=True,max_clamped=True,min_value=0, source = GPIO_COM_GUI)
    
    dpg.add_button(id="btn_toRunTest",label="Next Screen",callback=toRunTest)
    
    
    
    #RunTest - buttons needed to run and stop the test
    
    dpg.add_button(id="btn_runTest",label="Run Test",callback=runTest, show=False)
    
    dpg.add_input_int(id="int_stopTest",label="Stop Test",min_clamped=True,max_clamped=True,min_value=0,max_value=1, default_value=0, source = stopTest_GUI, show=False)
    
    dpg.add_input_int(id="int_removeExtensometer",label="Extensometer Removed? 0 = no, 1 = yes",min_clamped=True,max_clamped=True,min_value=0,max_value=1, default_value=0, source = removeExtensometer_GUI, show=False)
    
    #End test to write all data to file
    dpg.add_button(id="btn_toEndTest",label="End Test",callback=toEndTest, show=False)
    
    dpg.add_button(id="btn_toVirCOM",label="Back Screen",callback=toVirCOM, show=False)
    
    
    
    #endTest - What to show when testing has ended
    
    dpg.add_text("The test has ended. Please close the porgram using the red X in the top right corner",id="txt_endTest",show=False)
    
    #Main graphing Window
with dpg.window(id="Win_Plot", label="Plots", width=960, height=1080, no_close=True, no_collapse=True):
    
    #Elongation vs time graph
    with dpg.plot(label="Elongation", height=400, width=400):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", id="ETimeAxis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Elongation Inch", id="ElongationAxis")
        dpg.add_line_series(time_data, DSCUSB_data, label="Elongation", parent=dpg.last_item(), id="series_Elong")
    
    #Force vs time graph
    with dpg.plot(label="Force", height=400, width=400):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", id="FTimeAxis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Force", id="ForceAxis")
        dpg.add_line_series(time_data, LoadCell_data, label="Force", parent=dpg.last_item(), id="series_Force")

#Set primary window and start GUI
dpg.set_primary_window=("win_Main", True)
dpg.setup_dearpygui(viewport=vp)
dpg.show_viewport(vp)
dpg.start_dearpygui()