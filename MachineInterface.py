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
from multiprocessing import Process, Queue, Event
import MachineCommands as mc
# GPIO_COM = None
# GPIO = None 
# GPIO_IS_INIT = False

def consume_motor_commands(gpio, commandsQueue, stopEvent):
    while not stopEvent.is_set():
        # print("Process is running")
        if not commandsQueue.empty(): # new command to process
            next_command = commandsQueue.get()
            next_command(gpio) # these are blocking, so we can wait for them to complete
        else: # keep running previous command
            time.sleep(0.01)
        # run stop code
    mc.motor_stop(gpio)
    stopEvent.clear()
    while not commandsQueue.empty():
        commandsQueue.get()

class MachineController():
    def __init__(self, stopEvent):
        self.commandsQueue = Queue()
        self.stopEvent = stopEvent
        self.GPIO = None
        self.GPIO_COM = None
        self.GPIO_IS_INIT = False
        self.p = None

    def initGPIO(self):
        self.GPIO_COM = "COM"+str(dpg.get_value("GPIO_COM_GUI"))
        if self.p != None :
            self.stopEvent.set()
            print("Joining machine command consumer")
            self.p.join()
            self.p = None
            self.stopEvent.clear()
        try:
            self.GPIO = serial.Serial(self.GPIO_COM, 19200, timeout=1)
            self.GPIO.close()
            self.GPIO_IS_INIT = True
            print(f'GPIO_COM is {self.GPIO_COM}, GPIO is {self.GPIO}')
            self.p = Process(target = consume_motor_commands, name = "__child__", args = (self.GPIO, self.commandsQueue, self.stopEvent))        
            self.p.start()
            print("Consuming machine commands")
        except:
            self.GPIO_IS_INIT = False
            print(f'ERROR(MachineInterface.py): Unable to initialize GPIO at port {self.GPIO_COM}')


    def motor_up(self):
        print("Moving motor up")
        self.commandsQueue.put(mc.motor_up)
    def motor_down(self):
        print("Moving motor down")
        self.commandsQueue.put(mc.motor_down)
    def motor_stop(self):
        print("Stopping Motor")
        while not self.commandsQueue.empty():
            self.commandsQueue.get()
        self.commandsQueue.put(mc.motor_stop)
    def emergency_stop(self):
        print("EMERGENCY STOP")
        self.stopEvent.set() # tells process to stop

    def stop_process(self):
        if self.p != None:
            self.stopEvent.set()
            self.p.join()