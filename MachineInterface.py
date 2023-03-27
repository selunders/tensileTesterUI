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


class Proc_MachineController(Process):
    def __init__(self, commandsQueue, stopEvent):
        super(Proc_MachineController, self).__init__()
        self.commandsQueue = commandsQueue
        self.stopEvent = stopEvent
        self.GPIO = None
        self.GPIO_COM = None
        self.GPIO_IS_INIT = Event()
        self.GPIO_IS_INIT.clear()

    def run(self):
        while not self.stopEvent.is_set():
            # print("Process is running")
            if not self.commandsQueue.empty(): # new command to process
                next_command = self.commandsQueue.get()
                if not self.GPIO_IS_INIT.is_set():
                    print("ERROR(MachineInterface.py run()): GPIO is not initialized")
                    continue
                next_command(self) # these are blocking, so we can wait for them to complete
            else: # keep running previous command
                time.sleep(0.01)
        # run stop code
        mc.motor_stop()
        self.stopEvent.clear()
        self.commandsQueue.clear()

    def initGPIO(self):
        self.GPIO_COM = "COM"+str(dpg.get_value("GPIO_COM_GUI"))
        try:
            self.GPIO = serial.Serial(self.GPIO_COM, 19200, timeout=1)
            self.GPIO.close()
            self.GPIO_IS_INIT.set()
            print(f'GPIO_COM is {self.GPIO_COM}, GPIO is {self.GPIO}')
            return True
        except:
            print(f'ERROR(MachineInterface.py): Unable to initialize GPIO at port {self.GPIO_COM}')
            return False

    def motor_up(self):
        print("Moving motor up")
        self.commandsQueue.put(mc.motor_up)
    def motor_down(self):
        print("Moving motor down")
        self.commandsQueue.put(mc.motor_down)
    def motor_stop(self):
        print("Stopping Motor")
        self.commandsQueue.put(mc.motor_stop)
    def emergency_stop(self):
        print("EMERGENCY STOP")
        self.stopEvent.set() # tells process to stop

    def run_commands(self):
        self.stopEvent.clear()