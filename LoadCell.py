import serial

class LoadCellInterface():
    def __init__(self):
        self.LoadCell = None
        self.LoadCell_COM = None

    def init_load_cell(self, loadCell_COM):
        self.LoadCell_COM = loadCell_COM
        try:
            self.LoadCell = serial.Serial(port=self.LoadCell_COM, baudrate=115200, bytesize=8, stopbits=serial.STOPBITS_ONE)
            self.LoadCell.close()
            return True
        except:
            print(f"ERROR(LoadCell.py): Unable to open LoadCell port {self.LoadCell_COM}")
            self.LoadCell = None
            self.LoadCell_COM = None
            return False

    def ReadLoadCell(self):
        if self.LoadCell == None:
            return 9999999

        self.LoadCell.open()
        command = 'P\r'

        # for holding data from load cell
        data = ""

        # send command to load cell
        self.LoadCell.write(command.encode())

        #initialize data string with first read value
        data = self.LoadCell.read()

        # while the last character of the data string is NOT a return character, keep reading data
        while (data.decode("Ascii")[-1] != "\r"):
            data += self.LoadCell.read()
        #Close Serial port while not in use
        self.LoadCell.close()


        # parse data
        i = 0
        while(True):
            if(data.decode("Ascii")[i:i+1] == " "):
                break
            i += 1
        
        # get the float from the string
        floatData = float(data.decode("Ascii")[0:i])

        return floatData