import dearpygui.dearpygui as dpg
from multiprocessing import Queue, Event, Process
import serial, time

import Rotary_Encoder as RE
import LoadCell as LC

rotation_conversions_fromIndex = ["in", "cm", "mm"]

rotation_conversions = {
    "in": 0.00014,
    "cm": 0.000356, # calculated based on the 0.00014 number
    "mm": 0.00356 # calculated based on the 0.00014 number
}

conversion_factor = rotation_conversions["mm"]
# # print(__name__)
# if __name__ == "__main__":
# rotary_data = []
stop_event = Event()
converted_data = Queue()
data_from_rotary_encoder = Queue()
loadCell = LC.LoadCellInterface()

def init_load_cell():
    print(dpg.get_value("LOADCELL_COM_GUI"))
    loadCell.init_load_cell(dpg.get_value("LOADCELL_COM_GUI"))

def begin_re_and_temp_collection():
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

def collect_data(output_array_data, converted_output, output_array_time, loadcell_output):
    if data_from_rotary_encoder.empty():
        return False # No new data to collect
    else:
        while not data_from_rotary_encoder.empty():
            next_datapoint = data_from_rotary_encoder.get()
            # print("Data recieved: ", next_datapoint)
            output_array_data.append(next_datapoint['rotations'])
            converted_output.append(next_datapoint['rotations'] * conversion_factor)
            output_array_time.append(next_datapoint['time'])
            loadcell_output.append(loadCell.ReadLoadCell())
        return True # There is new data, it was collected