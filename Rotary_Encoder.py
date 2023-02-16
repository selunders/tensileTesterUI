from multiprocessing import Queue, Event
import serial
from time import sleep

def collect_data(queue, stop_event):
    # set up serial line
    ser = serial.Serial('COM10', 9600, timeout=1.0)
    sleep(2)

    # Read and record the data
    # data = []
    while not stop_event.is_set():
        b = ser.readline()          # read a byte string
        string_n = b.decode()       # decode byte string into Unicode
        string = string_n.rstrip()  # remove \n and \r (newlines)
        flt = string.split('\t')    # this is the character used by the arduino to divide data

        if len(flt) == 2:
            d = dict(rotations = int(flt[1]), time = float(flt[0]))
            # print("Rotary data: ", d)
            queue.put(d)
            # data.append(d)
    ser.close()