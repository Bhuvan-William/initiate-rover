import threading
import subprocess
import psutil
import Queue
from time import time

class PhantomOmni():
    def __init__(self, mode="mouse"):
        self.mode = mode
        
        #starts thread to run c script which talks to the arm
        self.dataThread = threading.Thread(target=self.getData)
        self.dataThread.setDaemon(True)
        self.dataThread.start()
        self.q = Queue.Queue()

    def run_commands(self, command):
        '''Runs given command in the shell in which the arm c script is running'''
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

    def getData(self):
        '''Starts the c script and constantly reads from stdout'''
        proc = subprocess.Popen(["cd /home/robot/Downloads/openhaptics_3.4-0-developer-edition-amd64/opt/OpenHaptics/Developer/3.4-0/examples/HD/console/paint/;./FrictionlessPlane"], stdout=subprocess.PIPE, shell=True)

        for stdout_line in iter(proc.stdout.readline, ""):
            self.q.put(stdout_line, block=False)

    def send_command(self, command):
        '''Writes to a file to communicate with certain scripts'''
        with open("/home/robot/Documents/yeet.txt", "w") as f:
            f.write(command)

    @property
    def coords(self):
        '''Reads from a file to get the coordinates of the arm'''
        while True:
            try:
                with open("/home/robot/Documents/yeet.txt", "r") as f:
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
        '''Checks if the arm is at the inkwell'''
        coords = self.coords
        if -1 < coords[0] < 1 and -66.5 < coords[1] < -64.5 and -88.5 < coords[2] < -87.5:
            return True
        return False

    def kill(self):
        '''Kills the c script in case of arm going out of control'''
        for proc in psutil.process_iter():
            if proc.name() == "FrictionlessPlane":
                proc.kill()