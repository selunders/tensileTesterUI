import dearpygui.dearpygui as dpg

from math import sin, cos

def print_me(sender):
    print(f"Menu Item: {sender}")

def print_value(sender):
    print(f'Value of {sender}: {dpg.get_value(sender)}')

cutoffMethod = "Force" # options: "Force", "Displacement"
def switchCutoffMethod(str):
    if str == "Force" or str == "Displacement":
        cutoffMethod = str

dpg.create_context()

with dpg.font_registry():
    default_font = dpg.add_font("fonts/DMMono-Regular.ttf", 20)
    header_font = dpg.add_font("fonts/DMMono-Regular.ttf", 25)
    second_font = dpg.add_font("fonts/SourceCodePro-LightItalic.ttf", 10)

#### Menu
# with dpg.viewport_menu_bar():
#     with dpg.menu(label="File"):
#         dpg.add_menu_item(label="Save", callback=print_me)
#         dpg.add_menu_item(label="Save As", callback=print_me)

#         with dpg.menu(label="Settings"):
#             dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
#             dpg.add_menu_item(label="Setting 2", callback=print_me)

#     dpg.add_menu_item(label="Help", callback=print_me)

#     with dpg.menu(label="Widget Items"):
#         dpg.add_checkbox(label="Pick Me", callback=print_me)
#         dpg.add_button(label="Press Me", callback=print_me)
#         dpg.add_color_picker(label="Color Me", callback=print_me)
###

#### SAMPLE DATA for plot
sindatax = []
sindatay = []
cosdatay = []
for i in range(100):
    sindatax.append(i/100)
    sindatay.append(0.5 + 0.5*sin(50*i/100))
    cosdatay.append(0.5 + 0.75*cos(50*i/100))
###

headers = []

with dpg.window(label="Main", tag="Main"):
    with dpg.table(header_row=False, row_background=False, borders_innerH=False, borders_outerH=False, borders_innerV=False, borders_outerV=False, resizable=True):
        dpg.add_table_column(label="Column 1")
        dpg.add_table_column(label="Column 2")

        # Two Columns, one Row

        with dpg.table_row():

            #
            with dpg.group(label="leftColumn"):

                ## Test Parameters Section ##
                headers.append(dpg.add_text("Test Parameters"))
                dpg.add_input_text(label="X-Section Area", decimal=True, callback=print_value)
                dpg.add_input_text(label="Width", decimal=True, callback=print_value)
                dpg.add_input_text(label="Height", decimal=True, callback=print_value)
                dpg.add_text("Stopping method:")
                with dpg.group(horizontal=True):
                    dpg.add_radio_button(("Force Based", "Displacement Based"), callback=print_value, horizontal=True)
                # if cutoffMethod == "Force":
                dpg.add_input_text(label="Force Cutoff", decimal=True)
                    # dpg.add_input_text(label="Displacement Cutoff", decimal=True)
                
                ## Initialization ##
                headers.append(dpg.add_text("Move Crosshead"))
                dpg.add_radio_button(("Fast", "Med", "Slow"), callback=print_value, horizontal=True)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Move UP", callback=print_me)
                    dpg.add_button(label="Move DOWN", callback=print_me)
                    dpg.add_button(label="STOP", callback=print_me)
                headers.append(dpg.add_text("Initialize Machine"))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Zero Force", callback=print_me)
                    dpg.add_button(label="Zero Displacement", callback=print_me)
                headers.append(dpg.add_text("Run Test"))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="BEGIN", callback=print_me)
                    dpg.add_button(label="PAUSE", callback=print_me)
                    # dpg.add_button(label="RESUME", callback=print_me)
                    dpg.add_button(label="STOP", callback=print_me)
                headers.append(dpg.add_text("Results"))
                with dpg.group():
                    dpg.add_checkbox(label="Export Graphs", default_value=True, callback=print_value)
                    dpg.add_checkbox(label="Export Test Parameters", callback=print_me)
                    dpg.add_text("Export Directory:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(default_value="~/tensile_results/", readonly=True, width=250)
                        dpg.add_button(label="Browse", callback=print_me)
                    dpg.add_button(label="Export Results", callback=print_me)
            # with dpg.table(header_row=True, row_background=True, borders_innerH=False, borders_outerH=False, borders_innerV=False, borders_outerV=False):
            with dpg.group(label="col2"):
                with dpg.plot(label="Force & Displacement", height=300, width=-1):
                            # optionally create legend
                            # dpg.add_plot_legend()
                            # REQUIRED: create x and y axes
                            dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                            with dpg.plot_axis(dpg.mvYAxis, label=""):
                                # series belong to a y axis
                                dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                with dpg.plot(label="Temperature", height=200, width=-1):
                            # dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
                            with dpg.plot_axis(dpg.mvYAxis, label="Temp (°C)"):
                                dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
                with dpg.plot(label="Stress/Strain Curve", height=200, width=-1):
                            # dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Strain")
                            with dpg.plot_axis(dpg.mvYAxis, label="Stress"):
                                dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")

    # Set Fonts
    dpg.bind_font(default_font)
    for header in headers:
        dpg.bind_item_font(header, header_font)

dpg.create_viewport(title='Run Tensile Test', width=800, height=750)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main", True)
dpg.start_dearpygui()
dpg.destroy_context()