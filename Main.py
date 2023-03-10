# Imports
import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue, Event

# Custom Modules
import FileManager as fm
import Data_Collection as dc

import UserTests
import UserHelp

if __name__ == "__main__":
    # Data
    rotary_encoder_data = []
    rotary_encoder_time = []


    dpg.create_context()


    dpg.add_file_dialog(directory_selector=True, show=False, callback=fm.callback, tag="file_dialog_id", cancel_callback=fm.cancel_callback, height=500)

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
            fm.export_data("Here's some sample data + params", params)
        else:
            fm.export_data("Here's some sample data")

    def load_params(parameterObject):
        dpg.set_value("x_section", parameterObject.x_section)
        dpg.set_value("width", parameterObject.width)
        dpg.set_value("height", parameterObject.height)

    cutoffMethod = "Force" # options: "Force", "Displacement"
    def switchCutoffMethod(str):
        if str == "Force" or str == "Displacement":
            cutoffMethod = str


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

    #### SAMPLE DATA for plot
    # sindatax = []
    # sindatay = []
    # cosdatay = []
    # for i in range(100):
    #     sindatax.append(i/100)
    #     sindatay.append(0.5 + 0.5*sin(50*i/100))
    #     cosdatay.append(0.5 + 0.75*cos(50*i/100))
    ###
    def FinalizeTest(sender):
        export_results(sender)
        UserTests.Print_Results(sender)

    headers = []
    dc.begin_data_collection()

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
                    headers.append(dpg.add_text("Specimen Parameters"))
                    dpg.add_input_text(label="(mm²) X-Section Area", decimal=True, callback=UserTests.HandleUserInput, user_data="xsection_area", tag="x_section_param")
                    dpg.add_input_text(label="(mm) Width", decimal=True, callback=UserTests.HandleUserInput, user_data="sample_width", tag="width_param")
                    dpg.add_input_text(label="(mm) Height", decimal=True, callback=UserTests.HandleUserInput, user_data="sample_height", tag="height_param")
                    
                    ## Initialization ##
                    dpg.add_separator()
                    headers.append(dpg.add_text("Test Parameters"))
                    dpg.add_text("Stopping method:")
                    with dpg.group(horizontal=True):
                        dpg.add_radio_button(("Force Based", "Displacement Based"), callback=UserTests.HandleUserInput, user_data="stopping_method", horizontal=True)
                    # if cutoffMethod == "Force":
                    dpg.add_input_text(label="(N) Force Cutoff", decimal=True, callback=UserTests.HandleUserInput, user_data="stopping_force", )
                        # dpg.add_input_text(label="Displacement Cutoff", decimal=True)
                    dpg.add_text("Manual Crosshead Controls:")
                    dpg.add_radio_button(("10mm/s", "5mm/s", "1mm/s"), callback=UserTests.SetMoveSpeed, horizontal=True)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Move UP", tag='btn_move_up')
                        dpg.add_button(label="Move DOWN", tag='btn_move_down')
                        dpg.add_button(label="STOP", callback=print_me)
                    dpg.add_separator()
                    headers.append(dpg.add_text("Initialize Machine"))
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Zero Force", callback=print_me)
                        dpg.add_button(label="Zero Displacement", callback=UserTests.ZeroDisplacement)
                    dpg.add_separator()
                    headers.append(dpg.add_text("Run Test"))
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="BEGIN", callback=print_me)
                        dpg.add_button(label="PAUSE", callback=print_me)
                        # dpg.add_button(label="RESUME", callback=print_me)
                        dpg.add_button(label="STOP", callback=print_me)
                    dpg.add_separator()
                    headers.append(dpg.add_text("Results"))
                    with dpg.group():
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
                                with dpg.plot_axis(dpg.mvXAxis, label="Displacement", tag="displacement_axis"):
                                    dpg.add_line_series(rotary_encoder_data, rotary_encoder_time, label="Displacement vs Time", tag="rotary_series_tag")
                                    dpg.set_axis_limits_auto("displacement_axis")
                                dpg.add_plot_axis(dpg.mvYAxis, label="Force", tag="force_axis")
                                dpg.set_axis_limits_auto("force_axis")
                                    # series belong to a y axis
                                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                                    # pass
                    with dpg.plot(label="", height=300, width=-1):
                                # dpg.add_plot_legend()
                                dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                                with dpg.plot_axis(dpg.mvYAxis, label="Temp (°C)"):
                                    pass
                                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                    with dpg.plot(label="", height=300, width=-1):
                                # dpg.add_plot_legend()
                                dpg.add_plot_axis(dpg.mvXAxis, label="Strain")
                                with dpg.plot_axis(dpg.mvYAxis, label="Stress"):
                                    pass
                                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")

        # Set Fonts
        dpg.bind_font(default_font)
        # We added each header to the headers list as it was created, so we can now easily manage all of them here:
        for header in headers:
            dpg.bind_item_font(header, header_font)

    dpg.create_viewport(title='Run Tensile Test', width=800, height=750)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Main", True)
    # dpg.start_dearpygui()

    while dpg.is_dearpygui_running():
        move_direction = 0
        # if force >= cutoff, stop!
        # if displacement >= cutoff, stop!
        if(dc.collect_data(rotary_encoder_data, rotary_encoder_time)):
            dpg.set_value('rotary_series_tag', [rotary_encoder_time, rotary_encoder_data])
        if(dpg.is_item_active('btn_move_up')):
            move_direction = -1
        elif(dpg.is_item_active('btn_move_down')):
            move_direction = 1
        else:
            move_direction = 0
        if(move_direction):
            UserTests.MoveCrossHead(move_direction, dpg.get_delta_time())
            # print(f"Moving {move_direction}. Time between frames: {dpg.get_delta_time()}")
        dpg.render_dearpygui_frame()

    dc.stop_data_collection()
    dpg.destroy_context()