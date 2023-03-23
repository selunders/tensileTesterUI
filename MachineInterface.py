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

stop_event = Event()
machine_commmands = Queue()

class Proc_MachineController(Process):
    def __init__(self, commandsQueue, stopEvent):
        super(Proc_MachineController, self).__init__()
        self.commandsQueue = commandsQueue
        self.stopEvent = stopEvent
        self.GPIO = None
        self.GPIO_COM = None
        self.GPIO_IS_INIT = False

    def run(self):
        if not self.GPIO_IS_INIT:
            print("ERROR(MachineInterface.py run()): GPIO is not initialized")
            return
        else:
            while not self.stopEvent.is_set():
                if not self.commandQueue.empty():
                    next_command = self.commandQueue.Dequeue()
                    next_command(self) # these are blocking, so we can wait for them to complete
                else:
                    time.sleep(0.01)

    def initGPIO(self, GPIO_COM):
        self.GPIO_COM = "COM"+str(dpg.get_value("GPIO_COM_GUI"))
        self.GPIO = serial.Serial(self.GPIO_COM, 19200, timeout=1)
        self.GPIO.close()
        self.GPIO_IS_INIT = True
        print(f'GPIO_COM is {self.GPIO_COM}, GPIO is {self.GPIO}')