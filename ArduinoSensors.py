from multiprocessing import Queue, Event, Process
import serial
from time import sleep
import dearpygui.dearpygui as dpg

class arduino_interface():
    def __init__(self, stopEvent, rotaryEncoderQueue, tempQueue):
        self.stop_event = stopEvent
        self.ser = None
        self.ser_com = None
        self.com_is_init = None
        self.re_queue = rotaryEncoderQueue
        self.p = None
        self.temp_queue = tempQueue
        # self.temp_process = None
        self.re_start_rotations = 0

    def initSerialPort(self):
        self.ser_com = "COM"+str(dpg.get_value("ARDUINO_COM_GUI"))
        if self.p != None :
            self.stopEvent.set()
            print("Joining Arduino Process")
            self.p.join()
            self.p = None
            self.stopEvent.clear()
        try:
            self.ser = serial.Serial(self.ser_com, 9600, timeout=1)
            sleep(1) # May or may not be necessary
            self.ser.close()
            self.com_is_init = True
            print(f'ser_com is {self.ser_com}, ser is {self.ser}')
            self.p = Process(target = self.collect_data, name = "__child__", args = ())        
            self.p.start()
            print("Reading from Arduino")
        except:
            self.com_is_init = False
            print(f'ERROR(ArduinoSensors.py): Unable to initialize Serial port {self.ser_com}')

    def collect_data(self):
        # Read and record the data
        while not self.stop_event.is_set():
            b = self.ser.readline()          # read a byte string
            string_n = b.decode()       # decode byte string into Unicode
            string = string_n.rstrip()  # remove \n and \r (newlines)
            flt = string.split('\t')    # this is the character used by the arduino to divide data

            match len(flt):
                case 3:
                    d = dict(rotations = int(flt[2]), time = float(flt[1]), data = flt[0])
                    self.re_queue.put(d)
                case 4:
                    d = dict(tempC = float(flt[2]), ambC = float(flt[3]), time = float(flt[1]), data = flt[0])
                    self.temp_queue.put(d)
                case _:
                    sleep(0.001)
        self.ser.close()
        return

# used to test IO ONLY, do not run in regular test
# def testIO():
#     ser = serial.Serial('COM10', 9600, timeout=1.0)
#     sleep(2)

#     # Read and record the data
#     # data = []
#     b = ser.readline()          # read a byte string
#     string_n = b.decode()       # decode byte string into Unicode
#     string = string_n.rstrip()  # remove \n and \r (newlines)
#     flt = string.split('\t')    # \t is the character used by the arduino to divide data
#     starting_rotations = 0

#     if len(flt) == 3:
#         d = dict(rotations = int(flt[2]), time = float(flt[1]), data = flt[0])
#         # print("Rotary data: ", d)
#         starting_rotations = d["rotations"]
#         # queue.put(d)
#         # data.append(d)

#     if len(flt) == 4:
#         d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
#         # print("Rotary data: ", d)
#         # queue.put(d)
#         # data.append(d)

#     while 1:
#         b = ser.readline()          # read a byte string
#         string_n = b.decode()       # decode byte string into Unicode
#         string = string_n.rstrip()  # remove \n and \r (newlines)
#         flt = string.split('\t')    # this is the character used by the arduino to divide data

#         if len(flt) == 3:
#             d = dict(rotations = int(flt[2]) - starting_rotations, time = float(flt[1]), data = flt[0])
#             # print("Rotary data: ", d)
#             #queue.put(d)
#         elif len(flt) == 4:
#             d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
#             # print("Thermocouple data: ", d)
#             #queue.put(d)
#         else:
#             sleep(0.001)