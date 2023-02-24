#Have the user first set the cross section area
#Have the user input the widthg and height
#Have the user set the stopping force cuttoff in Newtons of force that it will stop at
#Have the user set how much they want the crosshead to move down in mm/s and or set how many millimetters the user wants it to move down or move up or stop
#The user will then initialize the machine by zeroing either force or displacement or both.
#The user will then activate the test and have the option to pasue the test which will pause the machine but nbot pause data collection and or stop the test entirely.
#from the point once the test is done they will choose to either export the graphs or ecxport the test parameters(for future use).
#They will then choose the directory they want to send the files to and click export rresults to export them

xHeadMoveSpeed_mm = 15

Goals = {
    "xsection_area" : 20,
    "sample_width" : 2,
    "sample_height" : 6,
    "stopping_method" : "Force Based",
    "stopping_force" : 7000000,
    "crosshead_movestep" : 10,
    "crosshead_location" : -10,
    "displacement_zeroed" : True,
    "export_graphs" : True,
    "export_parameters" : True,
    "export_directory" : r"C:\Users\UI_ic\Desktop\tensileTesterUI\UserTests",
}

UserScore = {
    "xsection_area" : 0,
    "sample_width" : 0,
    "sample_height" : 0,
    "stopping_method" : "Force Based",
    "stopping_force" : 0,
    "crosshead_movestep" : 10,
    "crosshead_location" : 0,
    "displacement_zeroed" : False,
    "export_graphs" : 0,
    "export_parameters" : True,
    "export_directory" : 0,
}

def HandleUserInput(sender, app_data, user_data):
    UserScore[user_data] = app_data
    print(f'{sender} set UserScore[{user_data}] to {app_data}')

def MoveCrossHeadUp(sender):
    UserScore["crosshead_location"] -= UserScore["crosshead_movestep"]
    print(f'X-Head is now at {UserScore["crosshead_location"]}')
    UserScore["displacement_zeroed"] = False

def SetMoveSpeed(sender, app_data):
    match app_data:
        case "10mm":
            UserScore["crosshead_movestep"] = 10
        case "5mm":
            UserScore["crosshead_movestep"] = 5
        case "1mm":
            UserScore["crosshead_movestep"] = 1
    print(f'Setting X-Head move step to {UserScore["crosshead_movestep"]}mm')

def MoveCrossHeadDown(sender):
    UserScore["crosshead_location"] += UserScore["crosshead_movestep"]
    print(f'X-Head is now at {UserScore["crosshead_location"]}')
    UserScore["displacement_zeroed"] = False
    
def ZeroDisplacement(sender):
    UserScore["displacement_zeroed"] = True
    print("Displacement Zeroed")

def Print_Results(sender):
    print('Test: Goal | User')
    for key in Goals.keys():
        print(f'{key} : {Goals[key]} | {UserScore[key]}')