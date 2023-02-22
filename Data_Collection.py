from multiprocessing import Queue, Event, Process
import serial, time

import Rotary_Encoder as RE

# # print(__name__)
# if __name__ == "__main__":
# rotary_data = []
stop_event = Event()
data_from_rotary_encoder = Queue()

def begin_data_collection():
    stop_event.clear()
    p = Process(target = RE.collect_data, name = "__child__", args = (data_from_rotary_encoder, stop_event))
    p.start()

    # i = 0
    # while not stop_event.is_set():
    #     # if not data_from_rotary_encoder.empty():
    #     while not data_from_rotary_encoder.empty():
    #         next_datapoint = data_from_rotary_encoder.get()
    #         # print("Data recieved: ", next_datapoint)
    #         rotary_data.append(next_datapoint)
    #     time.sleep(1)
    #     # time.sleep(0.01)

def stop_data_collection():
    stop_event.set()

def collect_data(output_array_data, output_array_time):
    if data_from_rotary_encoder.empty():
        return False # No new data to collect
    else:
        while not data_from_rotary_encoder.empty():
            next_datapoint = data_from_rotary_encoder.get()
            # print("Data recieved: ", next_datapoint)
            output_array_data.append(next_datapoint['rotations'])
            output_array_time.append(next_datapoint['time'])
        return True # There is new data, it was collected