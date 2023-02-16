from multiprocessing import Queue, Event, Process
import serial

import Rotary_Encoder as RE

print(__name__)

if __name__ == "__main__":
    data_from_rotary_encoder = Queue()

    stop_event = Event()

    stop_event.clear()
    p = Process(target = RE.collect_data, name = "__child__", args = (data_from_rotary_encoder, stop_event))

    p.start()

    i = 0
    while not stop_event.is_set():
        if not data_from_rotary_encoder.empty():
            next_datapoint = data_from_rotary_encoder.get()
            print("Data recieved: ", next_datapoint)