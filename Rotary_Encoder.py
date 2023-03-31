from multiprocessing import Queue, Event
import serial
from time import sleep

def collect_data(queue, stop_event):
    # set up serial line
    ser = serial.Serial('COM10', 9600, timeout=1.0)
    sleep(2)

    # Read and record the data
    # data = []
    b = ser.readline()          # read a byte string
    string_n = b.decode()       # decode byte string into Unicode
    string = string_n.rstrip()  # remove \n and \r (newlines)
    flt = string.split('\t')    # \t is the character used by the arduino to divide data
    starting_rotations = 0

    if len(flt) == 3:
        d = dict(rotations = int(flt[2]), time = float(flt[1]), data = flt[0])
        # print("Rotary data: ", d)
        starting_rotations = d["rotations"]
        # queue.put(d)
        # data.append(d)

    if len(flt) == 4:
        d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
        # print("Rotary data: ", d)
        # queue.put(d)
        # data.append(d)

    while not stop_event.is_set():
        b = ser.readline()          # read a byte string
        string_n = b.decode()       # decode byte string into Unicode
        string = string_n.rstrip()  # remove \n and \r (newlines)
        flt = string.split('\t')    # this is the character used by the arduino to divide data

        if len(flt) == 3:
            d = dict(rotations = int(flt[2]) - starting_rotations, time = float(flt[1]), data = flt[0])
            queue.put(d)
        elif len(flt) == 4:
            d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
            queue.put(d)
        else:
            sleep(0.001)
    ser.close()


# used to test IO ONLY, do not run in regular test
def testIO():
    ser = serial.Serial('COM10', 9600, timeout=1.0)
    sleep(2)

    # Read and record the data
    # data = []
    b = ser.readline()          # read a byte string
    string_n = b.decode()       # decode byte string into Unicode
    string = string_n.rstrip()  # remove \n and \r (newlines)
    flt = string.split('\t')    # \t is the character used by the arduino to divide data
    starting_rotations = 0

    if len(flt) == 3:
        d = dict(rotations = int(flt[2]), time = float(flt[1]), data = flt[0])
        # print("Rotary data: ", d)
        starting_rotations = d["rotations"]
        # queue.put(d)
        # data.append(d)

    if len(flt) == 4:
        d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
        # print("Rotary data: ", d)
        # queue.put(d)
        # data.append(d)

    while 1:
        b = ser.readline()          # read a byte string
        string_n = b.decode()       # decode byte string into Unicode
        string = string_n.rstrip()  # remove \n and \r (newlines)
        flt = string.split('\t')    # this is the character used by the arduino to divide data

        if len(flt) == 3:
            d = dict(rotations = int(flt[2]) - starting_rotations, time = float(flt[1]), data = flt[0])
            print("Rotary data: ", d)
            #queue.put(d)
        elif len(flt) == 4:
            d = dict(tempC = float(flt[3]), ambC = float(flt[2]), time = float(flt[1]), data = flt[0])
            print("Thermocouple data: ", d)
            #queue.put(d)
        else:
            sleep(0.001)