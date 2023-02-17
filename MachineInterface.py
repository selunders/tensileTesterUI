# We need the following commands here or in other modules:
    # Motor
        # Move Motor Up
        # Move Motor Down
        # Stop Motor
    # Read Sensors
        # readDSCUSB
        # readLoadCell
    # Run Tests
        # runTest
        # endTest
    # IO
        # writeFile

def motor_down():
    clutchPin = 11
    GPIO.open()

    command = "gpio set " + chr(55 + int(clutchPin)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayEng)
    time.sleep(sleepGPIO)

    command = "gpio set " + "8" +"\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    
    GPIO.close()

def stopMotor():
    GPIO.open()

    command = "gpio clear 8\r"
    GPIO.write(command.encode())

    time.sleep(sleepRelayDiseng)
    time.sleep(sleepGPIO)

    command = "gpio clear " chr(55+int(11)) + "\r"
    GPIO.write(command.encode())

    time.sleep(sleepGPIO)
    command = "gpio set "+ chr(55 + int(12)) + "\r" #Set pin 12 [Clutch 3] = break
    GPIO.write(command.encode())
    
    time.sleep(1) #longer sleep time for break
    
    command = "gpio clear "+ chr(55 + int(12)) + "\r" #Clear pin 12 [Clutch 3] = break
    
    GPIO.write(command.encode())
    GPIO.close()