'''Class to interface with the geomagic touch via c scripts'''
import threading
import subprocess
import Queue
from time import time, sleep
import psutil

class PhantomOmni():

    #where to find the c scripts we wrote
    SCRIPTS_FOLDER = "/home/robot/Documents/server/home/rover/initiate/Phantom"
    SCRIPT_PATHS = {"plane" : "/FrictionlessPlane/;./FrictionlessPlane",
                    "forces": "/Jolt/;./FrictionlessPlane", 
                    "mouse" : "/Mouse/;./FrictionlessPlane",
                    "encoders" : "/RecordEncoders/;./Calibration",
                    "playback" : "/PlaybackEncoders/;./FrictionlessPlane",
                    "position" : "/RawValues/;./Calibration",
                    "gravity" : "/GravityMover/;./FrictionlessPlane"}

    def __init__(self, mode="mouse"):
        self.mode = mode
        self.procnames = ["Calibration", "FrictionlessPlane"]

        #starts the c scripts on another thread
        self.dataThread = threading.Thread(target=self.getData)
        self.dataThread.setDaemon(True)
        self.dataThread.start()
        self.q = Queue.Queue()


    def run_commands(self, command):
        '''Runs a given command in the shell in which the c script is running'''
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

    def getData(self):
        '''Starts the c script and reads from stdout'''
        proc = subprocess.Popen(["cd {}{}".format(PhantomOmni.SCRIPTS_FOLDER, PhantomOmni.SCRIPT_PATHS[self.mode])], stdout=subprocess.PIPE, shell=True)
        for stdout_line in iter(proc.stdout.readline, ""):
            self.q.put(stdout_line, block=False)

    def send_command(self, command):
        '''Writes to a file in order to talk to scripts which use multiples channels of communication'''
        with open("/home/robot/Documents/yeet.txt", "w") as f:
            f.write(command)

    @property
    def coords(self):
        '''Returns the coordinates of the arm'''
        '''
        print("begin")
        data = 0
        while True:
            try:
                t = time()
                data = self.q.get(block=False)
                x = time()-t
                print(x)
            except Queue.Empty:
                if data != 0:
                    break
                else:
                    print("caught up to queue")
        '''
        while True:
            try:
                with open("/home/robot/Documents/pos.txt", "r") as f:
                    data = f.read()

                parts = data.replace("\n", "").split(":")
                x = float(parts[0][1:])
                y = float(parts[1][1:])
                z = float(parts[2][1:])
                b1 = int(parts[3])
                b2 = int(parts[4])
                return (x, y, z, b1, b2)
            except ValueError:
                pass
        
    @property
    def encoders(self):
        '''Returns the encoder values of the arm'''
        while True:
            try:
                with open("/home/robot/Documents/encoders.txt", "r") as f:
                    data = f.read()

                parts = data.replace("\n", "").split(":")
                x = float(parts[0][1:])
                y = float(parts[1][1:])
                z = float(parts[2][1:])
                return (x, y, z)

            except ValueError:
                pass
                
    @property
    def x(self):
        coords = self.coords
        return coords[0]
    
    @property
    def y(self):
        coords = self.coords
        return coords[1]
    
    @property
    def z(self):
        coords = self.coords
        return coords[2]
    
    def ink(self):
        '''Returns whether the arm is in the inkwell or not'''
        coords = self.coords
        if -1 < coords[0] < 1 and -66.5 < coords[1] < -64.5 and -88.5 < coords[2] < -87.5:
            return True
        return False

    def jolt(self):
        self.send_command("J")
    
    def kill(self):
        '''Kills the relevant processes'''
        for proc in psutil.process_iter():
            if proc.name() in self.procnames:
                proc.kill()