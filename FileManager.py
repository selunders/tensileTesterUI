import dearpygui.dearpygui as dpg
import os

class FileManager:
    # directory_set_callback = None
    def load_directory(self, output_dir):
            self.output_directory = output_dir
            if os.path.exists(f"{output_dir}/params.json"):
                self.load_params_from_file(f"{output_dir}/params.json")
            else:
                print("Error in function 'load_directory' in FileManager class")

    def callback(self, sender, app_data):
        print(f"{sender} sent {app_data}")
        output_dir = app_data['file_path_name']
        if os.path.exists(output_dir):
            print("Directory exists! Loading information.")
            self.load_directory(output_dir)
        else:
            os.mkdir(output_dir)
            print(f"Creating directory {output_dir}")
            self.load_directory(output_dir)

    def cancel_callback(sender, app_data):
        print('Cancel clicked. Not changing directory path.')

    def export_data(self, data, test_params=""):
        if self.output_directory != "":
            if test_params:
                self.test_params_to_file(test_params)
            self.data_to_npy(data)
        else:
            print("ERROR(FileManager.export_data): No output directory specified.")

    def data_to_npy(self, data):
        print("WARNING(FileManager.data_to_npy): Not yet implemented.")

    def test_params_to_file(self, params):
        print("WARNING(FileManager.test_params_to_file): Not yet implemented.")
        # Write params to file.
        # Initial thought is to put a method that stores/loads params in an object.
        # That object is passed here, where it is written to the disk.

    def load_params_from_file(self, params):
        print("WARNING(FileManager.load_params_from_file): Not yet implemented.")

    def __init__(self):
        self.output_directory = None