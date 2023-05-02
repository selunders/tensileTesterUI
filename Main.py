# NOTE: to run on Raspberry Pi, you may need to run this in the terminal first: export MESA_GL_VERSION_OVERRIDE=4.5
# export MESA_GL_VERSION_OVERRIDE=4.5
# the dmesg command on linux will be very helpful in finding the right ttyACM and ttyUSB ports
# Imports
import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue, Event
from math import pi

# Custom Modules
import FileManager as fm
import Data_Collection as dc
import MachineInterface as machine_interface
import LoadCell as load_cell

import UserTests
import UserHelp

if __name__ == "__main__":
    # Data
    outputData = []
    rotary_encoder_data = []
    rotary_encoder_converted_distance = []
    rotary_encoder_time = []
    temp_time = []
    temp_data = []
    loadcell_data = []

    stress_data = []
    strain_data = []

    outputData.append(rotary_encoder_data)
    outputData.append(rotary_encoder_converted_distance)
    outputData.append(rotary_encoder_time)
    outputData.append(loadcell_data)
    outputData.append(temp_time)
    outputData.append(temp_data)
    outputData.append(stress_data)
    outputData.append(strain_data)
    
    cutoffMethod = "Force" # options: "Force", "Displacement"
    event_MachineStop = Event()
    event_MachineStop.clear()
    machineController = machine_interface.MachineController(event_MachineStop)

    dpg.create_context()
    
    dpg_headers = []
    dpg.add_file_dialog(directory_selector=True, show=False, callback=fm.callback, 
    tag="file_dialog_id", cancel_callback=fm.cancel_callback, height=500)

    def print_me(sender):
        print(f"Menu Item: {sender}")

    def print_value(sender):
        print(f'Value of {sender}: {dpg.get_value(sender)}')

    def export_results(sender):
        if(dpg.get_value("export_parameters_checkbox") == True):
            print("Attempting to export test data with parameters")
            params = fm.ParamData(
                x_section = dpg.get_value("x_section_param"),
                width = dpg.get_value("width_param"),
                height = dpg.get_value("height_param") 
                )
            fm.data_to_csv(rotary_encoder_converted_distance, rotary_encoder_time, loadcell_data, temp_time, temp_data, stress_data, strain_data)
        else:
            fm.data_to_csv(rotary_encoder_converted_distance, rotary_encoder_time, loadcell_data, temp_time, temp_data, stress_data, strain_data)

    def load_params(parameterObject):
        dpg.set_value("x_section", parameterObject.x_section)
        dpg.set_value("width", parameterObject.width)
        dpg.set_value("height", parameterObject.height)

    def switchCutoffMethod(str):
        # if str == "Force" or str == "Displacement" or str == "Both":
        global cutoffMethod
        cutoffMethod = str

    def calcSpecimenParams():
        # which_measurement = user_data
        width, height, x_section, thickness, radius = dpg.get_values(["width_param", "length_param", "x_section_param", "thickness_param", "radius_param"])
        # print(width, height, x_section, thickness, radius)
        match dpg.get_value("specimen_shape"):
            case "Rectangular":
                if not width or not height: return
                dpg.set_value("x_section_param", float(width) * float(thickness))
            case "Cylindrical":
                if not radius: return
                dpg.set_value("x_section_param", float(radius)*float(radius)*pi)

    def set_specimen_shape(sender, app_data):
        # Enables correct inputs for the chosen shape.
        match app_data:
            case "Rectangular":
                dpg.hide_item("radius_param")
                dpg.show_item("width_param")
                dpg.show_item("thickness_param")
            case "Cylindrical":
                dpg.show_item("radius_param")
                dpg.hide_item("width_param")
                dpg.hide_item("thickness_param")
        calcSpecimenParams()


    def check_limits(load_cell_force, displacement):
        try:
            should_stop = False
            if (load_cell_force >= dc.loadCell.LOADCELL_LIMIT_N):
                should_stop = True
            match dpg.get_value("stopping_method"):
                case "Force Based":
                    if(load_cell_force >= float(dpg.get_value('user_force_cutoff'))):
                        should_stop = True
                case "Displacement Based":
                    if(displacement >= float(dpg.get_value('user_displacement_cutoff'))):
                        should_stop = True
                case "Both":
                    if(displacement >= float(dpg.get_value('user_displacement_cutoff'))):
                        should_stop = True
                    if(load_cell_force >= float(dpg.get_value('user_force_cutoff'))):
                        should_stop = True
            if(should_stop):
                machineController.motor_stop()
                return False
            else:
                return True
        except:
            machineController.motor_stop()
            return False
        

    with dpg.font_registry():
        default_font = dpg.add_font("fonts/DMMono-Regular.ttf", 18)
        header_font = dpg.add_font("fonts/DMMono-Regular.ttf", 28)
        second_font = dpg.add_font("fonts/SourceCodePro-LightItalic.ttf", 10)

    # ### Menu
    with dpg.viewport_menu_bar():
    #     with dpg.menu(label="File"):
    #         dpg.add_menu_item(label="Save", callback=print_me)
    #         dpg.add_menu_item(label="Save As", callback=print_me)

    #         with dpg.menu(label="Settings"):
    #             dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
    #             dpg.add_menu_item(label="Setting 2", callback=print_me)

        dpg.add_menu_item(label="Help", callback=UserHelp.show_help_popup)

    #     with dpg.menu(label="Widget Items"):
    #         dpg.add_checkbox(label="Pick Me", callback=print_me)
    #         dpg.add_button(label="Press Me", callback=print_me)
    #         dpg.add_color_picker(label="Color Me", callback=print_me)
    # ##
    def convert_units(sender, app_data):
        rotary_encoder_converted_distance.clear()
        dc.conversion_factor = dc.rotation_conversions[app_data]
        for measurement in rotary_encoder_data:
            rotary_encoder_converted_distance.append(measurement * dc.conversion_factor)

    def control_machine(sender, app_data, user_data):
        if dpg.get_value("auto_mode") == "Auto":
            match user_data:
                case "move_up":
                    machineController.motor_up()
                case "move_down":
                    machineController.motor_down()

    def FinalizeTest(sender):
        export_results(sender)
        UserTests.Print_Results(sender)

    def InitArduino():
        temp_data.clear()
        temp_time.clear()
        rotary_encoder_converted_distance.clear()
        rotary_encoder_data.clear()
        loadcell_data.clear()
        dc.begin_re_and_temp_collection()

    def ResetTest(sender):
        for dataArray in outputData:
             dataArray.clear()
        dpg.set_value('rotary_series_tag', [rotary_encoder_converted_distance,loadcell_data])
        dpg.set_value('stress_strain_series_tag', [strain_data, stress_data])

        axes = ['temp_time_axis', 'temp_data_axis', 'displacement_axis', 'force_axis', 'stress_axis', 'strain_axis']
        for axis in axes:
            dpg.set_axis_limits(axis, 0, 2)
            dpg.fit_axis_data(axis)
            dpg.set_axis_limits_auto(axis)
        dc.zero_rotary_encoder()

    with dpg.window(label="Main", tag="Main"):
        dpg.add_spacer()
        dpg.add_spacer()
        dpg.add_spacer()
        with dpg.table(header_row=False, row_background=False, borders_innerH=False, borders_outerH=False, borders_innerV=False, borders_outerV=False, resizable=True):
            dpg.add_table_column(label="")
            dpg.add_table_column(label="")
            # Two Columns, one Row
            with dpg.table_row():
                with dpg.group(label="leftColumn"):

                    ## Specimen Parameters Section ##
                    dpg_headers.append(dpg.add_text("Initialize Machine"))
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Init LoadCell", callback=dc.init_load_cell)
                        dpg.add_input_text(label="Load Cell COM", decimal=False, callback=print_value, tag="LOADCELL_COM_GUI", width=25, no_spaces=True, default_value=7)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Init Machine", callback=machineController.initGPIO)
                        dpg.add_input_text(label="Machine COM", decimal=False, callback=print_value, tag="GPIO_COM_GUI", width=25, no_spaces=True, default_value=3)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Init Arduino", callback=InitArduino)
                        dpg.add_input_text(label="Arduino COM", decimal=False, callback=print_value, tag="ARDUINO_COM_GUI", width=25, no_spaces=True, default_value=10)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Zero Force", callback=dc.zero_load_cell)
                        dpg.add_button(label="Zero Displacement", callback=dc.zero_rotary_encoder)
                    dpg.add_separator()
                    dpg_headers.append(dpg.add_text("Specimen Parameters"))
                    dpg.add_radio_button(("Rectangular", "Cylindrical"), horizontal=True, tag="specimen_shape", callback=set_specimen_shape, default_value="Rectangular")
                    dpg.add_input_text(label="(mm) Initial Length", decimal=True, callback=calcSpecimenParams, user_data="specimen_length", tag="length_param", width=100, no_spaces=True, default_value=1.0)
                    dpg.add_input_text(label="(mm) Width", decimal=True, callback=calcSpecimenParams, user_data="specimen_width", tag="width_param", width=100, no_spaces=True, default_value=1.0)
                    dpg.add_input_text(label="(mm) Thickness", decimal=True, callback=calcSpecimenParams, user_data="specimen_thickness", tag="thickness_param", width=100, no_spaces=True, default_value=1.0)
                    dpg.hide_item(dpg.add_input_text(label="(mm) Radius", decimal=True, callback=calcSpecimenParams, user_data="specimen_radius", tag="radius_param", width=100, no_spaces=True, default_value=1.0))
                    dpg.add_input_text(label="(mm²) X-Section Area", decimal=True, callback=calcSpecimenParams, user_data="xsection_area", tag="x_section_param", width=100, no_spaces=True, default_value=1.0, readonly=True)
                    
                    ## Initialization ##
                    dpg.add_separator()
                    dpg_headers.append(dpg.add_text("Test Parameters"))
                    dpg.add_text("Stopping method:")
                    with dpg.group(horizontal=True):
                        dpg.add_radio_button(("Off","Force Based", "Displacement Based", "Both"), tag="stopping_method", horizontal=False, default_value="Off")
                    # if cutoffMethod == "Force":
                    dpg.add_input_text(label="(N) Force Cutoff", decimal=True, width=50, tag="user_force_cutoff")
                    dpg.add_input_text(label="(mm) Displacement Cutoff", decimal=True, width=50, tag="user_displacement_cutoff")
                        # dpg.add_input_text(label="Displacement Cutoff", decimal=True)
                    dpg.add_separator()
                    dpg_headers.append(dpg.add_text("Run Test"))
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="RESET", callback=ResetTest)
                        # dpg.add_button(label="BEGIN", callback=print_me)
                        # dpg.add_button(label="PAUSE", callback=print_me)
                        # dpg.add_button(label="RESUME", callback=print_me)
                        # dpg.add_button(label="STOP", callback=print_me)
                    dpg.add_text("Manual Crosshead Controls:")
                    dpg.add_radio_button(("Auto", "Manual"), horizontal=True, tag="auto_mode", callback=print_value, default_value="Auto")
                    # dpg.add_radio_button(("10mm/s", "5mm/s", "1mm/s"), callback=UserTests.SetMoveSpeed, horizontal=True)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Move UP", callback=control_machine, user_data="move_up",tag='btn_move_up')
                        dpg.add_button(label="Move DOWN", callback=control_machine, user_data="move_down", tag='btn_move_down')
                        dpg.add_button(label="STOP", callback=machineController.motor_stop)
                    dpg.add_separator()
                    dpg_headers.append(dpg.add_text("Results"))
                    with dpg.group():
                        # dpg.add_text("Export Units:")
                        # with dpg.group(horizontal=True):
                            # dpg.add_radio_button(("mm", "cm", "in"), callback=convert_units, horizontal=True)
                        dpg.add_checkbox(label="Export Graphs", default_value=True, callback=UserTests.HandleUserInput, user_data="export_graphs")
                        dpg.add_checkbox(label="Export Test Parameters", tag="export_parameters_checkbox", default_value=True, callback=UserTests.HandleUserInput, user_data="export_parameters")
                        dpg.add_text("Export Directory:")
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(default_value="", tag="export_folder_text_box",readonly=True, width=250)
                            dpg.add_button(label="Browse", callback=lambda: dpg.show_item("file_dialog_id"))
                        dpg.add_button(label="Export Results", callback=FinalizeTest)
                # with dpg.table(header_row=True, row_background=True, borders_innerH=False, borders_outerH=False, borders_innerV=False, borders_outerV=False):
                with dpg.group(label="col2"):
                    with dpg.plot(label="", height=400, width=-1):
                                # optionally create legend
                                # dpg.add_plot_legend()
                                # REQUIRED: create x and y axes
                                with dpg.plot_axis(dpg.mvXAxis, label="Displacement (mm)", tag="displacement_axis"):
                                    dpg.add_line_series(rotary_encoder_data, rotary_encoder_time, label="Displacement vs Time", tag="rotary_series_tag")
                                    dpg.set_axis_limits_auto("displacement_axis")
                                dpg.add_plot_axis(dpg.mvYAxis, label="Force (N)", tag="force_axis")
                                dpg.set_axis_limits_auto("force_axis")
                                    # series belong to a y axis
                                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                                    # pass
                    with dpg.plot(label="", height=200, width=-1):
                                # dpg.add_plot_legend()
                                with dpg.plot_axis(dpg.mvXAxis, label="Time (s)", tag="temp_time_axis"):
                                    dpg.add_line_series(strain_data, stress_data, label="Temp (C) vs Time", tag="temp_time_series_tag")
                                    dpg.set_axis_limits_auto("temp_time_axis")
                                    # dpg.set_axis_limits('temp_time_axis', max(temp_time) - 5, max(temp_time) + 1)
                                dpg.add_plot_axis(dpg.mvYAxis, label="Temp (C)", tag="temp_data_axis")
                                dpg.set_axis_limits_auto("temp_data_axis")
                    # with dpg.plot(label="", height=300, width=-1):
                    #             # dpg.add_plot_legend()
                    #             dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                    #             with dpg.plot_axis(dpg.mvYAxis, label="Temp (°C)"):
                    #                 pass
                                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                    with dpg.plot(label="", height=300, width=-1):
                                # dpg.add_plot_legend()
                                with dpg.plot_axis(dpg.mvXAxis, label="Strain (mm/mm)", tag="strain_axis"):
                                    dpg.add_line_series(strain_data, stress_data, label="Stress vs Strain", tag="stress_strain_series_tag")
                                    dpg.set_axis_limits_auto("strain_axis")
                                dpg.add_plot_axis(dpg.mvYAxis, label="Stress (MPa)", tag="stress_axis")
                                dpg.set_axis_limits_auto("stress_axis")

        # Set Fonts
        dpg.bind_font(default_font)
        # We added each header to the headers list as it was created, so we can now easily manage all of them here:
        for header in dpg_headers:
            dpg.bind_item_font(header, header_font)

    dpg.create_viewport(title='Run Tensile Test', width=800, height=750)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Main", True)
    # dpg.start_dearpygui()

    while dpg.is_dearpygui_running():
        # if force >= cutoff, stop!
        # if displacement >= cutoff, stop!
        if(dc.collect_re_data(rotary_encoder_data, rotary_encoder_converted_distance, loadcell_data)):
            dpg.set_value('rotary_series_tag', [rotary_encoder_converted_distance,loadcell_data])
            dpg.fit_axis_data('displacement_axis')
            dpg.fit_axis_data('force_axis')

            stress_data.append(float(loadcell_data[-1]) / float(dpg.get_value('x_section_param')))
            strain_data.append(float(rotary_encoder_converted_distance[-1])/float(dpg.get_value('length_param')))
            dpg.set_value('stress_strain_series_tag', [strain_data, stress_data])
            dpg.fit_axis_data('stress_axis')
            dpg.fit_axis_data('strain_axis')

        if(dc.collect_temp_data(temp_data, temp_time)):
             # Not showing first value. Used for baseline time.
             dpg.set_value('temp_time_series_tag', [temp_time[1:], temp_data[1:]])
             dpg.set_axis_limits('temp_time_axis', max(temp_time) - 60, max(temp_time))
            #  dpg.set_axis_limits('temp_data_axis', temp_data[-1] - 5, temp_data[-1] + 5)
             dpg.fit_axis_data('temp_time_axis')
             dpg.fit_axis_data('temp_data_axis')

        if dpg.get_value("auto_mode") == "Manual":
            if(dpg.is_item_active('btn_move_up')):
                if not machineController.motor_is_running:
                    machineController.motor_up()
            elif(dpg.is_item_active('btn_move_down')):
                if not machineController.motor_is_running:
                    machineController.motor_down()
            else:
                if machineController.motor_is_running:
                    machineController.motor_stop()
        # print(len(loadcell_data), len(rotary_encoder_converted_distance), motor_is_running)
        if len(loadcell_data) > 0 and len(rotary_encoder_converted_distance) > 0 and machineController.motor_is_running:
            # print(f"Current force: {loadcell_data[-1]}")
            check_limits(loadcell_data[-1], rotary_encoder_converted_distance[-1])

        dpg.render_dearpygui_frame()

    dc.stop_data_collection()
    machineController.stop_process()
    dpg.destroy_context()


    # Newtons, mm
    # MPa, strain is unitless (generally). mm/mm for polymers, for aluminum: microstrains?