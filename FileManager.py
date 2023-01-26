import dearpygui.dearpygui as dpg
import os

class ParamData:
    def __init__(self, x_section = "", width = "", height = ""):
        self.x_section = x_section
        self.width = width
        self.height = height
    def __str__(self):
        return f"""
        X-Section: {self.x_section}
        Width: {self.width}
        Height: {self.height}
        """

output_directory = None

def load_directory(output_dir):
        output_directory = output_dir
        if os.path.exists(f"{output_directory}/params.json"):
            get_params_from_file(f"{output_directory}/params.json")
            print(f"Directory {output_dir} loaded. Params loaded from params.json file.")
        else:
            print(f"Directory {output_dir} loaded. No params.json file located.")
        dpg.set_value("export_folder_text_box", output_directory)


def callback(sender, app_data):
    print(f"{sender} sent {app_data}")
    # print(sender['file_path_name'])
    output_dir = app_data['file_path_name']
    if os.path.exists(output_dir):
        print("Directory exists! Loading information.")
        load_directory(output_dir)
    else:
        os.mkdir(output_dir)
        print(f"Creating directory {output_dir}")
        load_directory(output_dir)

def cancel_callback(sender, app_data):
    print('Cancel clicked. Not changing directory path.')

def export_data(data, test_params=""):
    # print("ERROR(FileManager.export_data): No output directory specified.")
    if output_directory != "":
        print(f"Exporting to {output_directory}")
        if test_params:
            test_params_to_file(test_params)
        data_to_npy(data)
    else:
        print("ERROR(FileManager.export_data): No output directory specified.")

def data_to_npy(data):
    print("WARNING(FileManager.data_to_npy): Not yet implemented.")
    print(f" Got data {data}")

def test_params_to_file(params):
    print("WARNING(FileManager.test_params_to_file): Not yet implemented.")
    print(f" Got params {params}")
    # Write params to file.
    # Initial thought is to put a method that stores/loads params in an object.
    # That object is passed here, where it is written to the disk.

def get_params_from_file(params):
    print("WARNING(FileManager.load_params_from_file): Not yet implemented.")