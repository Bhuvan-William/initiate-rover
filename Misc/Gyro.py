'''Gyro class for getting values from the gyroscope'''
import serial

class Gyro:
    def __init__(self):
        #initialise serial connection
        self.ser = serial.Serial('/dev/ttyUSB0') 
        self.ser.baudrate = 9600
        self.x = 0
        self.y = 0
        self.z = 0
    
    def getValues(self):
        '''Read via serial from the arduino nano'''
        try:
            vals = self.ser.readline().split(":")
            coords = [int(i) for i in vals[:3]]
            return coords
        except ValueError:
            return None

    def close(self):
        self.ser.close()
    