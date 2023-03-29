import time

sleepGPIO = 0.05 #Time for GPIO to process previous command
sleepRelayEng = .015 #Time for relays to engage
sleepRelayDiseng = .010 #Time for relays to disengage

########
# NOTE: GPIO_IS_INIT is handled in MachineInterface.py
########

def motor_down(GPIO):
    # if not GPIO_IS_INIT:
    #     print("GPIO not initialized")
    #     return
    clutchPin = 11 #clutch number 1
    GPIO.open()

    command = "gpio set " + chr(55 + int(clutchPin)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayEng)
    time.sleep(sleepGPIO)

    command = "gpio set " + "8" +"\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    # 
    GPIO.close()

def motor_up(GPIO):
    # if not GPIO_IS_INIT:
    #     print("GPIO not initialized")
    #     return
    clutchPin = 14 # clutch number 4
    GPIO.open()

    command = "gpio set " + chr(55 + int(clutchPin)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayEng)
    time.sleep(sleepGPIO)

    command = "gpio set " + "8" +"\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    
    GPIO.close()


def motor_stop(GPIO):
    # if not GPIO_IS_INIT:
    #     print("GPIO not initialized")
    #     return
    GPIO.open()

    command = "gpio clear 8\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayDiseng)
    time.sleep(sleepGPIO)

    command = "gpio clear " + chr(55+int(11)) + "\r"
    GPIO.write(command.encode())

    command = "gpio clear " + chr(55+int(14)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    command = "gpio set " + chr(55 + int(12)) + "\r" #Set pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    time.sleep(1) #longer sleep time for break
    
    command = "gpio clear " + chr(55 + int(12)) + "\r" #Clear pin 12 [Clutch 3] = break
    
    GPIO.write(command.encode())
    GPIO.close()

    # Direction
    # Pausing
    # Fix axis labels, check
    # Report some data from the test?
    # Force cutoff/displacement
    # Initializing machine